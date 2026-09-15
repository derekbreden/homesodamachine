#pragma once

#include "proto_msg.h"

namespace j9_query_policy {

// Four queued announcements can take eight 500 ms dark-display polls when
// prime snapshots alternate with news. Leave another second for the reply.
constexpr uint32_t kEnclosureReplyWaitMs = 5000;

class PrimeQueryReplies {
public:
    // Endpoint renews the real session and emits at most one frame from each
    // send method. A changed snapshot always wins. Discovery queries receive
    // an absolute snapshot immediately; only a live lease can yield to news.
    template <typename Endpoint>
    bool handle(uint8_t type, const uint8_t *payload, uint16_t len,
                Endpoint &endpoint) {
        if (type != MSG_PRIME_SESSION_QUERY ||
            len < sizeof(PrimeSessionQueryPayload)) return false;
        PrimeSessionQueryPayload query;
        memcpy(&query, payload, sizeof(query));
        const bool matching = endpoint.renewSession(query.sessionToken);
        if (endpoint.sendChangedState()) {
            deferred_ = false;
        } else if (matching && !deferred_ && endpoint.sendAnnouncement()) {
            // The next query must return state even if more news is queued.
            // At 500 ms polling this bounds the snapshot gap to 1000 ms,
            // below the enclosure's 1800 ms stale-state threshold.
            deferred_ = true;
        } else {
            endpoint.sendState();
            deferred_ = false;
        }
        return true;
    }

private:
    bool deferred_ = false;
};

}  // namespace j9_query_policy
