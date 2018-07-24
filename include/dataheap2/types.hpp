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
#include <dataheap2/datachunk.pb.h>

namespace dataheap2
{
using Value = double;

struct TimeValue
{
    TimeValue() = default;

    constexpr TimeValue(TimePoint t, Value v) : time(t), value(v){};
    TimePoint time;
    Value value;

    operator DataChunk() const
    {
        DataChunk dc;
        dc.add_time_delta(time.time_since_epoch().count());
        dc.add_value(value);
        return dc;
    }
};

template <typename T>
void data_chunk_foreach(const DataChunk& dc, T cb)
{
    int64_t timestamp = 0;
    auto value_iter = dc.value().begin();
    for (const auto& time_delta : dc.time_delta())
    {
        timestamp += time_delta;
        cb(dataheap2::TimeValue(dataheap2::TimePoint(dataheap2::Duration(timestamp)), *value_iter));
        value_iter++;
    }
}

class DataChunkIter
{
public:
    DataChunkIter(
        google::protobuf::RepeatedField<const google::protobuf::int64>::iterator iter_time,
        google::protobuf::RepeatedField<const double>::iterator iter_value)
    : iter_time(iter_time), iter_value(iter_value)
    {
    }

    dataheap2::TimeValue operator*() const
    {
        return { dataheap2::TimePoint(dataheap2::Duration(timestamp + *iter_time)), *iter_value };
    }

    DataChunkIter& operator++()
    {
        timestamp += *iter_time;
        iter_time++;
        iter_value++;
        return *this;
    }

    bool operator!=(const DataChunkIter& other)
    {
        return iter_time != other.iter_time;
    }

private:
    google::protobuf::RepeatedField<const google::protobuf::int64>::iterator iter_time;
    google::protobuf::RepeatedField<const double>::iterator iter_value;
    int64_t timestamp = 0;
};

inline DataChunkIter begin(const DataChunk& dc)
{
    return { dc.time_delta().begin(), dc.value().begin() };
}

inline DataChunkIter end(const DataChunk& dc)
{
    return { dc.time_delta().end(), dc.value().end() };
}
} // namespace dataheap2
