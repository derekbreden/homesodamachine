#include <unity.h>

#include "sound_policy.h"

using namespace sound_policy;

void setUp() {}
void tearDown() {}

static Settings loud() {
    Settings s;
    s.volume = 100;
    s.quietOn = true;
    s.quietStart = 22;
    s.quietEnd = 7;
    s.quietVolume = 0;
    return s;
}

// The one property the whole file exists to hold: no setting reaches the alarm.
// Every volume, every quiet window, every hour including no clock at all.
void test_no_setting_can_silence_an_unsilenceable_sound() {
    for (uint16_t volume = 0; volume <= 100; volume++) {
        for (uint16_t quietVolume = 0; quietVolume <= 100; quietVolume++) {
            Settings s;
            s.volume = (uint8_t)volume;
            s.quietVolume = (uint8_t)quietVolume;
            for (uint8_t on = 0; on <= 1; on++) {
                s.quietOn = on != 0;
                for (int hour = kNoHour; hour <= 23; hour++) {
                    TEST_ASSERT_EQUAL_UINT8(100, levelFor(s, hour, true));
                }
            }
        }
    }
}

// And the mirror of it: everything else is reachable by volume alone.
void test_volume_zero_silences_every_other_sound() {
    Settings s;
    s.volume = 0;
    s.quietOn = false;
    for (int hour = kNoHour; hour <= 23; hour++) {
        TEST_ASSERT_EQUAL_UINT8(0, levelFor(s, hour, false));
    }
}

void test_quiet_hours_hold_a_sound_down_to_their_ceiling() {
    Settings s = loud();
    s.quietVolume = 25;
    TEST_ASSERT_EQUAL_UINT8(25, levelFor(s, 23, false));   // inside the window
    TEST_ASSERT_EQUAL_UINT8(100, levelFor(s, 12, false));  // outside it
}

// A ceiling above the volume is not a floor: quiet hours only ever quieten.
void test_a_quiet_ceiling_above_the_volume_does_not_raise_it() {
    Settings s = loud();
    s.volume = 30;
    s.quietVolume = 80;
    TEST_ASSERT_EQUAL_UINT8(30, levelFor(s, 23, false));
}

// 22:00-07:00 is the default and it wraps midnight.
void test_the_window_wraps_midnight() {
    Settings s = loud();
    TEST_ASSERT_TRUE(inQuietHours(s, 22));
    TEST_ASSERT_TRUE(inQuietHours(s, 23));
    TEST_ASSERT_TRUE(inQuietHours(s, 0));
    TEST_ASSERT_TRUE(inQuietHours(s, 6));
    TEST_ASSERT_FALSE(inQuietHours(s, 7));    // the end hour is outside
    TEST_ASSERT_FALSE(inQuietHours(s, 21));
}

void test_a_window_that_does_not_wrap_is_the_hours_between_its_ends() {
    Settings s = loud();
    s.quietStart = 9;
    s.quietEnd = 17;
    TEST_ASSERT_FALSE(inQuietHours(s, 8));
    TEST_ASSERT_TRUE(inQuietHours(s, 9));
    TEST_ASSERT_TRUE(inQuietHours(s, 16));
    TEST_ASSERT_FALSE(inQuietHours(s, 17));
}

// Without a believable clock they never engage. A machine that guessed at the
// hour in order to go quiet would go quiet at the wrong one.
void test_no_clock_means_no_quiet_hours() {
    Settings s = loud();
    TEST_ASSERT_FALSE(inQuietHours(s, kNoHour));
    TEST_ASSERT_EQUAL_UINT8(100, levelFor(s, kNoHour, false));
}

// Both ends the same hour is an empty window, not a whole day.
void test_a_window_with_the_same_ends_is_empty() {
    Settings s = loud();
    s.quietStart = s.quietEnd = 13;
    for (int hour = 0; hour <= 23; hour++) TEST_ASSERT_FALSE(inQuietHours(s, hour));
}

void test_quiet_hours_off_is_off_at_every_hour() {
    Settings s = loud();
    s.quietOn = false;
    for (int hour = 0; hour <= 23; hour++) TEST_ASSERT_FALSE(inQuietHours(s, hour));
}

void test_a_value_out_of_range_is_a_value_never_written() {
    Settings s;
    s.volume = 200;
    s.quietVolume = 101;
    s.quietStart = 24;
    s.quietEnd = 99;
    s = clamped(s);
    TEST_ASSERT_EQUAL_UINT8(100, s.volume);
    TEST_ASSERT_EQUAL_UINT8(100, s.quietVolume);
    TEST_ASSERT_EQUAL_UINT8(0, s.quietStart);
    TEST_ASSERT_EQUAL_UINT8(0, s.quietEnd);
}

// Full loudness leaves the step's own duty where the table put it.
void test_a_full_factor_plays_the_duty_the_table_states() {
    for (uint8_t duty = 1; duty <= SOUND_MAX_DUTY; duty++)
        TEST_ASSERT_UINT8_WITHIN(1, duty, dutyForFactor(duty, 1.0f));
}

// The claim the header makes: the control is linear in amplitude, so half
// loudness is well below half duty, not at it.
void test_halving_the_loudness_halves_the_amplitude_not_the_duty() {
    const uint8_t full = dutyForFactor(SOUND_MAX_DUTY, 1.0f);
    const uint8_t half = dutyForFactor(SOUND_MAX_DUTY, 0.5f);
    TEST_ASSERT_EQUAL_UINT8(SOUND_MAX_DUTY, full);
    TEST_ASSERT_TRUE(half < full / 2);          // duty falls faster than loudness
    TEST_ASSERT_TRUE(half > 0);
}

// Monotone in the factor, and never above the drive's ceiling.
void test_duty_rises_with_the_factor_and_stops_at_the_ceiling() {
    uint8_t last = 0;
    for (int pct = 1; pct <= 100; pct++) {
        const uint8_t d = dutyForFactor(SOUND_MAX_DUTY, (float)pct / 100.0f);
        TEST_ASSERT_TRUE(d >= last);
        TEST_ASSERT_TRUE(d <= SOUND_MAX_DUTY);
        last = d;
    }
    TEST_ASSERT_EQUAL_UINT8(SOUND_MAX_DUTY, dutyForFactor(SOUND_MAX_DUTY, 4.0f));
}

// A sound that is not silenced makes something: no rounding sends it to zero.
void test_a_nonzero_factor_always_makes_something() {
    for (uint8_t duty = 1; duty <= SOUND_MAX_DUTY; duty++)
        TEST_ASSERT_TRUE(dutyForFactor(duty, 0.01f) > 0);
    TEST_ASSERT_EQUAL_UINT8(0, dutyForFactor(0, 1.0f));
    TEST_ASSERT_EQUAL_UINT8(0, dutyForFactor(SOUND_MAX_DUTY, 0.0f));
}

int main(int, char **) {
    UNITY_BEGIN();
    RUN_TEST(test_no_setting_can_silence_an_unsilenceable_sound);
    RUN_TEST(test_volume_zero_silences_every_other_sound);
    RUN_TEST(test_quiet_hours_hold_a_sound_down_to_their_ceiling);
    RUN_TEST(test_a_quiet_ceiling_above_the_volume_does_not_raise_it);
    RUN_TEST(test_the_window_wraps_midnight);
    RUN_TEST(test_a_window_that_does_not_wrap_is_the_hours_between_its_ends);
    RUN_TEST(test_no_clock_means_no_quiet_hours);
    RUN_TEST(test_a_window_with_the_same_ends_is_empty);
    RUN_TEST(test_quiet_hours_off_is_off_at_every_hour);
    RUN_TEST(test_a_value_out_of_range_is_a_value_never_written);
    RUN_TEST(test_a_full_factor_plays_the_duty_the_table_states);
    RUN_TEST(test_halving_the_loudness_halves_the_amplitude_not_the_duty);
    RUN_TEST(test_duty_rises_with_the_factor_and_stops_at_the_ceiling);
    RUN_TEST(test_a_nonzero_factor_always_makes_something);
    return UNITY_END();
}
