#include <unity.h>

#include "flavor_selection.h"
#include "flavor_link_policy.h"

using namespace flavor_selection;

namespace {

void test_new_controller_is_unestablished_and_not_falsely_persisted() {
    Authority authority;
    TEST_ASSERT_EQUAL_UINT8(0, authority.selected());
    TEST_ASSERT_FALSE(authority.established());
    TEST_ASSERT_FALSE(authority.needsPersistence());
    TEST_ASSERT_FALSE(authority.persisted());
}

void test_valid_persisted_selection_establishes_controller_authority() {
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

void test_later_sync_cannot_overwrite_established_controller_state() {
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

void test_selection_establishes_a_controller_without_saved_state() {
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

void test_accepted_but_not_durable_state_reasserts_after_controller_reboot() {
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

void test_request_token_is_idempotent_inside_one_controller_session() {
    flavor_link_policy::TokenLedger ledger;
    TEST_ASSERT_FALSE(ledger.duplicateOrRemember(0x12345678));
    TEST_ASSERT_TRUE(ledger.duplicateOrRemember(0x12345678));
    TEST_ASSERT_FALSE(ledger.duplicateOrRemember(0x87654321));
    TEST_ASSERT_TRUE(ledger.duplicateOrRemember(0x87654321));

    ledger.reset();
    TEST_ASSERT_FALSE(ledger.duplicateOrRemember(0x87654321));
}

}  // namespace

void setUp() {}
void tearDown() {}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_new_controller_is_unestablished_and_not_falsely_persisted);
    RUN_TEST(test_valid_persisted_selection_establishes_controller_authority);
    RUN_TEST(test_corrupt_persisted_selection_is_treated_as_absent);
    RUN_TEST(test_first_sync_adopts_the_faucet_saved_selection);
    RUN_TEST(test_later_sync_cannot_overwrite_established_controller_state);
    RUN_TEST(test_absolute_selection_is_idempotent);
    RUN_TEST(test_selection_establishes_a_controller_without_saved_state);
    RUN_TEST(test_persistence_success_clears_dirty_and_error);
    RUN_TEST(test_invalid_wire_values_never_change_selection);
    RUN_TEST(test_clean_connected_epoch_synchronizes_cached_state);
    RUN_TEST(test_even_number_of_unanswered_taps_reasserts_final_absolute_state);
    RUN_TEST(test_accepted_but_not_durable_state_reasserts_after_controller_reboot);
    RUN_TEST(test_final_connected_level_after_same_service_reconnect_still_gets_an_action);
    RUN_TEST(test_request_token_is_idempotent_inside_one_controller_session);
    return UNITY_END();
}
