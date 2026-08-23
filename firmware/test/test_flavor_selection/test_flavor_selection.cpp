#include <unity.h>

#include "flavor_selection.h"
#include "flavor_link_policy.h"

using namespace flavor_selection;

namespace {

void test_new_main_board_is_unestablished_and_not_falsely_persisted() {
    Authority authority;
    TEST_ASSERT_EQUAL_UINT8(0, authority.selected());
    TEST_ASSERT_FALSE(authority.established());
    TEST_ASSERT_FALSE(authority.needsPersistence());
    TEST_ASSERT_FALSE(authority.persisted());
}

void test_valid_persisted_selection_establishes_main_board_authority() {
    Authority authority;
    TEST_ASSERT_EQUAL(Update::Changed, authority.loadPersisted(1));
    TEST_ASSERT_EQUAL_UINT8(1, authority.selected());
    TEST_ASSERT_TRUE(authority.established());
    TEST_ASSERT_TRUE(authority.persisted());
}

void test_corrupt_persisted_selection_is_treated_as_absent() {
    Authority authority;
    authority.loadPersisted(1);
    TEST_ASSERT_EQUAL(Update::Rejected, authority.loadPersisted(2));
    TEST_ASSERT_FALSE(authority.established());
    TEST_ASSERT_EQUAL_UINT8(0, authority.selected());
}

void test_first_sync_adopts_the_faucet_saved_selection() {
    Authority authority;
    TEST_ASSERT_EQUAL(Update::Changed, authority.synchronize(1));
    TEST_ASSERT_EQUAL_UINT8(1, authority.selected());
    TEST_ASSERT_TRUE(authority.established());
    TEST_ASSERT_TRUE(authority.needsPersistence());
    TEST_ASSERT_FALSE(authority.persisted());
}

void test_later_sync_cannot_overwrite_established_main_board_state() {
    Authority authority;
    authority.loadPersisted(1);
    TEST_ASSERT_EQUAL(Update::Unchanged, authority.synchronize(0));
    TEST_ASSERT_EQUAL_UINT8(1, authority.selected());
    TEST_ASSERT_TRUE(authority.persisted());
}

void test_absolute_selection_is_idempotent() {
    Authority authority;
    authority.loadPersisted(0);
    TEST_ASSERT_EQUAL(Update::Unchanged, authority.select(0));
    TEST_ASSERT_FALSE(authority.needsPersistence());

    TEST_ASSERT_EQUAL(Update::Changed, authority.select(1));
    TEST_ASSERT_TRUE(authority.needsPersistence());
    TEST_ASSERT_EQUAL(Update::Unchanged, authority.select(1));
    TEST_ASSERT_TRUE(authority.needsPersistence());
}

void test_selection_establishes_a_main_board_without_saved_state() {
    Authority authority;
    TEST_ASSERT_EQUAL(Update::Changed, authority.select(0));
    TEST_ASSERT_TRUE(authority.established());
    TEST_ASSERT_TRUE(authority.needsPersistence());
}

void test_persistence_success_clears_dirty_and_error() {
    Authority authority;
    authority.select(1);
    authority.persistenceFinished(false);
    TEST_ASSERT_TRUE(authority.needsPersistence());
    TEST_ASSERT_TRUE(authority.persistenceError());
    TEST_ASSERT_FALSE(authority.persisted());

    authority.persistenceFinished(true);
    TEST_ASSERT_FALSE(authority.needsPersistence());
    TEST_ASSERT_FALSE(authority.persistenceError());
    TEST_ASSERT_TRUE(authority.persisted());
}

void test_invalid_wire_values_never_change_selection() {
    Authority authority;
    authority.loadPersisted(1);
    TEST_ASSERT_EQUAL(Update::Rejected, authority.synchronize(2));
    TEST_ASSERT_EQUAL(Update::Rejected, authority.select(255));
    TEST_ASSERT_EQUAL_UINT8(1, authority.selected());
    TEST_ASSERT_TRUE(authority.persisted());
}

void test_clean_connected_epoch_synchronizes_cached_state() {
    TEST_ASSERT_EQUAL(
        static_cast<int>(flavor_link_policy::EpochAction::Synchronize),
        static_cast<int>(flavor_link_policy::epochAction(true, false, false, false, 1, 1)));
}

void test_even_number_of_unanswered_taps_reasserts_final_absolute_state() {
    // B -> A can end at the last acknowledged A. The queued-selection bit is
    // what distinguishes those two taps from a connection with no local work.
    TEST_ASSERT_EQUAL(
        static_cast<int>(flavor_link_policy::EpochAction::Reassert),
        static_cast<int>(flavor_link_policy::epochAction(true, false, false, true, 0, 0)));
}

void test_accepted_but_not_durable_state_reasserts_after_main_board_reboot() {
    TEST_ASSERT_EQUAL(
        static_cast<int>(flavor_link_policy::EpochAction::Reassert),
        static_cast<int>(flavor_link_policy::epochAction(true, false, true, false, 1, 1)));
}

void test_final_connected_level_after_same_service_reconnect_still_gets_an_action() {
    // A DISCONNECTED + CONNECTED callback pair increments the transport
    // generation twice. The adapter observes "changed, final level true" and
    // feeds that final level here instead of relying on a level edge.
    TEST_ASSERT_EQUAL(
        static_cast<int>(flavor_link_policy::EpochAction::Synchronize),
        static_cast<int>(flavor_link_policy::epochAction(true, false, false, false, 0, 0)));
}

void test_main_board_revision_publishes_immediately() {
    TEST_ASSERT_TRUE(flavor_link_policy::mainBoardStatePublicationDue(
        true, true, true, 101, 100, 500));
}

void test_main_board_heartbeat_republishes_absolute_state() {
    TEST_ASSERT_FALSE(flavor_link_policy::mainBoardStatePublicationDue(
        true, true, false, 599, 100, 500));
    TEST_ASSERT_TRUE(flavor_link_policy::mainBoardStatePublicationDue(
        true, true, false, 600, 100, 500));
}

void test_main_board_heartbeat_is_safe_across_millis_rollover() {
    TEST_ASSERT_FALSE(flavor_link_policy::mainBoardStatePublicationDue(
        true, true, false, 0x00000010u, 0xFFFFFF00u, 500));
    TEST_ASSERT_TRUE(flavor_link_policy::mainBoardStatePublicationDue(
        true, true, false, 0x00000100u, 0xFFFFFF00u, 500));
}

void test_main_board_never_publishes_unestablished_first_install_default() {
    TEST_ASSERT_FALSE(flavor_link_policy::mainBoardStatePublicationDue(
        true, false, true, 10000, 0, 500));
    TEST_ASSERT_FALSE(flavor_link_policy::mainBoardStatePublicationDue(
        true, false, false, 10000, 0, 500));
}

void test_main_board_does_not_publish_while_transport_is_down() {
    TEST_ASSERT_FALSE(flavor_link_policy::mainBoardStatePublicationDue(
        false, true, true, 10000, 0, 500));
}

void test_main_board_heartbeat_confirms_a_lost_tokenized_reply_immediately() {
    // The controller's repeated absolute B is enough to settle a faucet
    // request for B even if the matching tokenized response was lost.
    TEST_ASSERT_TRUE(flavor_link_policy::mainBoardHeartbeatSettlesPendingSelection(
        false, true, false, 1, 1, 100, 0, 2250));
}

void test_conflicting_heartbeat_waits_through_the_retry_grace() {
    TEST_ASSERT_FALSE(flavor_link_policy::mainBoardHeartbeatSettlesPendingSelection(
        false, true, true, 1, 0, 2249, 0, 2250));
    TEST_ASSERT_TRUE(flavor_link_policy::mainBoardHeartbeatSettlesPendingSelection(
        false, true, true, 1, 0, 2250, 0, 2250));
}

void test_conflicting_heartbeat_cannot_replace_unsent_or_offline_work() {
    TEST_ASSERT_FALSE(flavor_link_policy::mainBoardHeartbeatSettlesPendingSelection(
        false, true, false, 1, 0, 10000, 0, 2250));
    TEST_ASSERT_FALSE(flavor_link_policy::mainBoardHeartbeatSettlesPendingSelection(
        true, true, true, 1, 1, 10000, 0, 2250));
}

void test_main_board_heartbeat_grace_is_rollover_safe() {
    TEST_ASSERT_FALSE(flavor_link_policy::mainBoardHeartbeatSettlesPendingSelection(
        false, true, true, 1, 0, 0x00000010u, 0xFFFFFF00u, 300));
    TEST_ASSERT_TRUE(flavor_link_policy::mainBoardHeartbeatSettlesPendingSelection(
        false, true, true, 1, 0, 0x00000100u, 0xFFFFFF00u, 300));
}

void test_callback_consumes_epoch_before_sync_survives_post_service_check() {
    uint32_t knownGeneration = 7;
    bool synchronized = false;

    // TinyProto may announce CONNECTED and dispatch the first SYNC frame from
    // one service call. Callback entry must consume the generation first.
    if (flavor_link_policy::consumeConnectionEpoch(8, knownGeneration))
        synchronized = false;
    synchronized = true;  // The callback successfully applies SYNC.

    // Cleanup after service sees the same generation and must not erase the
    // synchronization established by that frame.
    if (flavor_link_policy::consumeConnectionEpoch(8, knownGeneration))
        synchronized = false;

    TEST_ASSERT_TRUE(synchronized);
    TEST_ASSERT_EQUAL_UINT32(8, knownGeneration);
}

void test_request_token_history_keeps_delayed_retries_idempotent() {
    flavor_link_policy::TokenLedger ledger;
    TEST_ASSERT_FALSE(ledger.duplicateOrRemember(0x12345678));
    TEST_ASSERT_TRUE(ledger.duplicateOrRemember(0x12345678));
    TEST_ASSERT_FALSE(ledger.duplicateOrRemember(0x87654321));
    TEST_ASSERT_TRUE(ledger.duplicateOrRemember(0x87654321));

    for (uint32_t i = 0; i < flavor_link_policy::kRecentTokenCapacity - 2; ++i)
        TEST_ASSERT_FALSE(ledger.duplicateOrRemember(0xA0000000u + i));

    // The first request is still recognized after later maintenance traffic
    // has replaced the ledger's most-recent token many times.
    TEST_ASSERT_TRUE(ledger.duplicateOrRemember(0x12345678));

    // One more new token evicts the oldest entry from the fixed history.
    TEST_ASSERT_FALSE(ledger.duplicateOrRemember(0xB0000000u));
    TEST_ASSERT_FALSE(ledger.duplicateOrRemember(0x12345678));

    ledger.reset();
    TEST_ASSERT_FALSE(ledger.duplicateOrRemember(0x87654321));
}

}  // namespace

void setUp() {}
void tearDown() {}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_new_main_board_is_unestablished_and_not_falsely_persisted);
    RUN_TEST(test_valid_persisted_selection_establishes_main_board_authority);
    RUN_TEST(test_corrupt_persisted_selection_is_treated_as_absent);
    RUN_TEST(test_first_sync_adopts_the_faucet_saved_selection);
    RUN_TEST(test_later_sync_cannot_overwrite_established_main_board_state);
    RUN_TEST(test_absolute_selection_is_idempotent);
    RUN_TEST(test_selection_establishes_a_main_board_without_saved_state);
    RUN_TEST(test_persistence_success_clears_dirty_and_error);
    RUN_TEST(test_invalid_wire_values_never_change_selection);
    RUN_TEST(test_clean_connected_epoch_synchronizes_cached_state);
    RUN_TEST(test_even_number_of_unanswered_taps_reasserts_final_absolute_state);
    RUN_TEST(test_accepted_but_not_durable_state_reasserts_after_main_board_reboot);
    RUN_TEST(test_final_connected_level_after_same_service_reconnect_still_gets_an_action);
    RUN_TEST(test_main_board_revision_publishes_immediately);
    RUN_TEST(test_main_board_heartbeat_republishes_absolute_state);
    RUN_TEST(test_main_board_heartbeat_is_safe_across_millis_rollover);
    RUN_TEST(test_main_board_never_publishes_unestablished_first_install_default);
    RUN_TEST(test_main_board_does_not_publish_while_transport_is_down);
    RUN_TEST(test_main_board_heartbeat_confirms_a_lost_tokenized_reply_immediately);
    RUN_TEST(test_conflicting_heartbeat_waits_through_the_retry_grace);
    RUN_TEST(test_conflicting_heartbeat_cannot_replace_unsent_or_offline_work);
    RUN_TEST(test_main_board_heartbeat_grace_is_rollover_safe);
    RUN_TEST(test_callback_consumes_epoch_before_sync_survives_post_service_check);
    RUN_TEST(test_request_token_history_keeps_delayed_retries_idempotent);
    return UNITY_END();
}
