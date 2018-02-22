#include <dataheap2/sink.hpp>

#include <amqpcpp.h>

#include <nlohmann/json.hpp>

#include <iostream>

namespace dataheap2
{
using json = nlohmann::json;

Sink::Sink(const std::string& token, struct ev_loop* loop) : Connection(token, loop)
{
}

void Sink::config_callback(const json& config)
{
    std::cout << "Start parsing config" << std::endl;

    if (data_connection_)
    {
        if (config["dataServerAddress"] != data_server_address_)
        {
            std::cerr << "Changing dataServerAddress on the fly is not currently supported.\n";
            std::abort();
        }
        if (config["dataQueue"] != data_queue_)
        {
            std::cerr << "Changing dataQueue on the fly is not currently supported.\n";
            std::abort();
        }
    }

    const std::string& data_server_address_ = config["dataServerAddress"];
    data_queue_ = config["dataQueue"];

    data_connection_ =
        std::make_unique<AMQP::TcpConnection>(&handler, AMQP::Address(data_server_address_));
    data_channel_ = std::make_unique<AMQP::TcpChannel>(data_connection_.get());
    data_channel_->onError(
        [](const char* message) { std::cerr << "data channel error: " << message << std::endl; });

    data_channel_
        ->declareQueue(data_queue_) //  rpc queue
        .onSuccess([this](const std::string& name, int msgcount, int consumercount) {
            // callback function that is called when the consume operation starts
            auto startCb = [](const std::string& consumertag) {
                std::cout << "consume operation started" << std::endl;
            };

            // callback function that is called when the consume operation failed
            auto errorCb = [](const char* message) {
                std::cerr << "consume operation failed" << std::endl;
            };

            // callback operation when a message was received
            auto messageCb = [this](const AMQP::Message& message, uint64_t deliveryTag,
                                    bool redelivered) {
                data_callback(message);
                data_channel_->ack(deliveryTag);
            };

            data_channel_->consume(name).onReceived(messageCb).onSuccess(startCb).onError(errorCb);
        });

    if (config.find("sinkConfig") != config.end())
    {
        sink_config_callback(config["sinkConfig"]);
    }
    ready_callback();
}

void Sink::data_callback(const AMQP::Message& message)
{
    if (message.bodySize() < 2)
    {
        return;
    }

    const auto& metric_name = message.routingkey();
    auto message_string = std::string(message.body(), message.bodySize());
    MessageCoding message_coding = static_cast<MessageCoding>(message_string.front());

    message_string.erase(0, 1);

    switch (message_coding)
    {
    case MessageCoding::single:
    {
        DataPoint datapoint;
        datapoint.ParseFromString(message_string);
        data_callback(metric_name, datapoint);
        break;
    }
    case MessageCoding::chunk:
    {
        DataChunk datachunk;
        datachunk.ParseFromString(message_string);
        data_callback(metric_name, datachunk);
        break;
    }
    }
}
}