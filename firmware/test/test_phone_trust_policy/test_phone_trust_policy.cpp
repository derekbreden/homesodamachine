#include <unity.h>
#include "../../src_faucet/trust_policy.h"

using namespace phone_trust_policy;

void setUp() {}
void tearDown() {}

static void a_legacy_request_has_an_absolute_minute_even_when_repeated() {
    RequestWindow request;
    request.open(0, false);
    TEST_ASSERT_FALSE(request.expired(59999));
    TEST_ASSERT_TRUE(request.renew(59999));
    TEST_ASSERT_EQUAL_UINT32(1, request.remaining(59999));
    TEST_ASSERT_TRUE(request.expired(60000));
    TEST_ASSERT_FALSE(request.renew(60000));
}

static void a_presence_lease_expires_and_renewal_never_moves_the_ceiling() {
    RequestWindow request;
    request.open(0, true);
    TEST_ASSERT_FALSE(request.expired(14999));
    TEST_ASSERT_TRUE(request.expired(15000));
    TEST_ASSERT_FALSE(request.renew(15000));

    request.open(100000, true);
    for (uint32_t now = 105000; now < 160000; now += 5000) {
        TEST_ASSERT_TRUE(request.renew(now));
        TEST_ASSERT_EQUAL_UINT32(160000 - now, request.remaining(now));
    }
    TEST_ASSERT_TRUE(request.expired(160000));
    request.close();
    TEST_ASSERT_TRUE(request.expired(160001));
}

static void an_unsuccessful_end_has_a_global_quiet_gap() {
    RateLimit limits;
    limits.admitted(11, 0);
    limits.unsuccessful(1000);  // timeout, withdrawal, or disconnect
    TEST_ASSERT_EQUAL_INT((int)Refusal::busy, (int)limits.check(11, 1001).refusal);
    TEST_ASSERT_EQUAL_UINT32(14999, limits.check(99, 1001).retryMs);
    TEST_ASSERT_FALSE(limits.check(99, 15999).allowed());
    TEST_ASSERT_TRUE(limits.check(99, 16000).allowed());
}

static void a_declined_identity_keeps_its_pause_across_new_connections() {
    RateLimit limits;
    const uint64_t identity = 0x01020304050607ULL;
    limits.admitted(identity, 0);
    limits.declined(identity, 10);
    TEST_ASSERT_EQUAL_INT((int)Refusal::declined, (int)limits.check(identity, 15010).refusal);
    TEST_ASSERT_EQUAL_UINT32(15000, limits.check(identity, 15010).retryMs);
    TEST_ASSERT_TRUE(limits.check(777, 15010).allowed());
    // Admission is keyed only by the bonded identity: a new connection,
    // generation or pairing key cannot supply a different rate-limit key.
    TEST_ASSERT_FALSE(limits.check(identity, 30009).allowed());
    TEST_ASSERT_TRUE(limits.check(identity, 30010).allowed());
}

static void successive_physical_declines_escalate_and_quiet_resets_them() {
    RateLimit limits;
    uint32_t now = 100;
    const uint32_t own[] = {30000, 120000, 600000, 1800000};
    const uint32_t global[] = {15000, 60000, 300000, 1800000};
    for (unsigned i = 0; i < 4; ++i) {
        limits.admitted(11, now);
        limits.declined(11, now);
        TEST_ASSERT_EQUAL_UINT32(own[i], limits.check(11, now).retryMs);
        TEST_ASSERT_EQUAL_UINT32(global[i], limits.check(22, now).retryMs);
        now += own[i];
    }
    now += kResetMs;
    limits.service(now);
    limits.admitted(11, now);
    limits.declined(11, now);
    TEST_ASSERT_EQUAL_UINT32(30000, limits.check(11, now).retryMs);
    TEST_ASSERT_EQUAL_UINT32(15000, limits.check(22, now).retryMs);
}

static void rotating_identities_still_obey_global_decline_backoff() {
    RateLimit limits;
    uint32_t now = 0;
    const uint32_t global[] = {15000, 60000, 300000, 1800000};
    for (unsigned i = 0; i < 4; ++i) {
        const uint64_t identity = i + 1;
        TEST_ASSERT_TRUE(limits.check(identity, now).allowed());
        limits.admitted(identity, now);
        limits.declined(identity, now);
        TEST_ASSERT_EQUAL_UINT32(global[i], limits.check(1000 + i, now).retryMs);
        now += global[i];
    }
}

static void rejected_spam_neither_extends_time_nor_evicts_a_penalty() {
    RateLimit limits;
    limits.admitted(11, 0);
    limits.declined(11, 0);
    for (uint32_t now = 1; now < 30000; ++now) {
        const Admission waiting = limits.check(11, now);
        TEST_ASSERT_EQUAL_UINT32(30000 - now, waiting.retryMs);
        (void)limits.check(1000 + now, now);
    }
    TEST_ASSERT_TRUE(limits.check(11, 30000).allowed());

    // Even physical decisions filling the table do not evict a live entry.
    for (uint64_t identity = 100; identity < 120; ++identity) limits.declined(identity, 30001);
    limits.declined(11, 30002);
    limits.approved(999, 30003);  // clears the global pause, not another phone's
    TEST_ASSERT_EQUAL_INT((int)Refusal::declined, (int)limits.check(11, 30003).refusal);
    TEST_ASSERT_EQUAL_UINT32(119999, limits.check(11, 30003).retryMs);
}

static void only_an_actual_approval_resets_the_relevant_policy() {
    RateLimit limits;
    limits.declined(11, 0);
    TEST_ASSERT_FALSE(limits.check(11, 1).allowed());
    // An already-trusted no-op does not call approved().
    (void)limits.check(22, 1);
    TEST_ASSERT_FALSE(limits.check(11, 2).allowed());
    limits.approved(11, 3);
    TEST_ASSERT_TRUE(limits.check(11, 3).allowed());
    TEST_ASSERT_TRUE(limits.check(22, 3).allowed());
}

static void deadlines_and_second_rounding_survive_millis_wrap() {
    const uint32_t start = UINT32_MAX - 9999;
    RequestWindow request;
    request.open(start, true);
    TEST_ASSERT_TRUE(request.renew(start + 5000));
    TEST_ASSERT_FALSE(request.expired(start + 19999));
    TEST_ASSERT_TRUE(request.expired(start + 20000));
    RateLimit limits;
    limits.declined(11, start);
    TEST_ASSERT_EQUAL_UINT32(20000, limits.check(11, start + 10000).retryMs);
    TEST_ASSERT_TRUE(limits.check(11, start + 30000).allowed());
    TEST_ASSERT_EQUAL_UINT16(1, seconds(1));
    TEST_ASSERT_EQUAL_UINT16(1, seconds(1000));
    TEST_ASSERT_EQUAL_UINT16(2, seconds(1001));
}

static void a_restart_drops_rate_state_and_does_not_model_pairing_storage() {
    RateLimit before;
    before.declined(11, 1000);
    TEST_ASSERT_FALSE(before.check(11, 1001).allowed());
    RateLimit restarted;
    TEST_ASSERT_TRUE(restarted.check(11, 0).allowed());
    // Approved pairing storage is owned separately by phone_trust.cpp; this
    // RAM policy neither erases nor fabricates any trusted-phone record.
}

int main() {
    UNITY_BEGIN();
    RUN_TEST(a_legacy_request_has_an_absolute_minute_even_when_repeated);
    RUN_TEST(a_presence_lease_expires_and_renewal_never_moves_the_ceiling);
    RUN_TEST(an_unsuccessful_end_has_a_global_quiet_gap);
    RUN_TEST(a_declined_identity_keeps_its_pause_across_new_connections);
    RUN_TEST(successive_physical_declines_escalate_and_quiet_resets_them);
    RUN_TEST(rotating_identities_still_obey_global_decline_backoff);
    RUN_TEST(rejected_spam_neither_extends_time_nor_evicts_a_penalty);
    RUN_TEST(only_an_actual_approval_resets_the_relevant_policy);
    RUN_TEST(deadlines_and_second_rounding_survive_millis_wrap);
    RUN_TEST(a_restart_drops_rate_state_and_does_not_model_pairing_storage);
    return UNITY_END();
}
