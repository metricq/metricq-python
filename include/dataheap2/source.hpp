// Copyright (c) 2018, ZIH,
// Technische Universitaet Dresden,
// Federal Republic of Germany
//
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without modification,
// are permitted provided that the following conditions are met:
//
//     * Redistributions of source code must retain the above copyright notice,
//       this list of conditions and the following disclaimer.
//     * Redistributions in binary form must reproduce the above copyright notice,
//       this list of conditions and the following disclaimer in the documentation
//       and/or other materials provided with the distribution.
//     * Neither the name of metricq nor the names of its contributors
//       may be used to endorse or promote products derived from this software
//       without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
// EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#pragma once
#include <dataheap2/chrono.hpp>
#include <dataheap2/connection.hpp>
#include <dataheap2/datachunk.pb.h>
#include <dataheap2/source_metric.hpp>
#include <dataheap2/types.hpp>

#include <amqpcpp.h>

#include <nlohmann/json.hpp>

#include <memory>
#include <string>

namespace ev
{
class timer;
}

namespace dataheap2
{

class Source : public Connection
{
public:
    Source(const std::string& token);
    ~Source();

    void send(const std::string& id, TimeValue tv);
    void send(const std::string& id, const DataChunk& dc);

    SourceMetric& operator[](const std::string& id)
    {
        auto ret = metrics_.try_emplace(id, id, *this);
        return ret.first->second;
    }

protected:
    void setup_complete() override;
    void send_metrics_list();
    virtual void source_config_callback(const nlohmann::json& config) = 0;
    virtual void ready_callback() = 0;
    void close() override;

private:
    void config_callback(const nlohmann::json& config);

private:
    AMQP::LibAsioHandler data_handler_;
    std::unique_ptr<AMQP::TcpConnection> data_connection_;
    std::unique_ptr<AMQP::TcpChannel> data_channel_;
    std::string data_exchange_;
    std::string data_server_address_;

    std::unordered_map<std::string, SourceMetric> metrics_;
};
} // namespace dataheap2
