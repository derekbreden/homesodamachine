#include <cassert>
#include <cmath>
#include <cstdio>
#include "motion_policy.h"
#include "command_input.h"
#include "safety_policy.h"
#include "tmc_protocol.h"
using namespace pgfun_positioner;
Health good(){ return Health{true,0,true,true,false}; }
void establish(MotionPolicy &m,uint64_t now=1000){auto h=good();assert(m.clear(1,now,h));assert(m.reference(2,now,h));assert(m.arm(3,now,h));}
void jog_test(){
 MotionPolicy m;auto h=good();establish(m);assert(!m.move(4,1000,100000,{256,0},h));
 assert(m.move(4,1000,1000000,{256,-128},h));unsigned edges[2]={};
 for(uint64_t t=1250;t<=1011000;t+=250){if(t%100000==0)assert(m.ping(m.last_sequence+1,t));auto mask=m.tick(t,h);for(unsigned a=0;a<2;++a)if(mask&(1u<<a))++edges[a];}
 assert(m.state==State::Armed);assert(m.count[0]==256 && m.count[1]==-128);assert(edges[0]==256 && edges[1]==128);
 assert(m.completed_sequence==4);assert(!m.move(m.last_sequence+1,1020000,1000000,{257,0},h));
 h.stop_closed=false;assert(m.tick(1020250,h)==0);assert(m.fault==Fault::Stop && !m.referenced());
}
void independent_faults(){
 for(int f=0;f<5;++f){MotionPolicy m;auto h=good();establish(m);
  if(f==0)h.open_limit_mask=2;if(f==1)h.motor_supply_ok=false;if(f==2)h.drivers_ok=false;
  if(f==3){assert(m.tick(501000,h)==0);assert(m.fault==Fault::HostTimeout);continue;}
  if(f==4){assert(m.move(4,1000,1000000,{64,0},h));assert(m.tick(10000,h)==0);assert(m.fault==Fault::Timing);continue;}
  assert(m.tick(1250,h)==0);assert(!m.enabled() && !m.referenced());
 }
}
void trajectory_test(){
 MotionPolicy m;auto h=good();establish(m);uint32_t seq=4;const unsigned n=64;const uint32_t period=8000000;
 assert(m.load(seq++,1000,period,n));assert(!m.knot(seq,1000,1,0,0));
 for(unsigned i=0;i<n;++i)assert(m.knot(seq++,1000,i,int(std::round(100*std::sin(i*2*3.141592653589793/n))),0));
 h.pedal_pressed=true;assert(!m.play(seq,1000,h));h.pedal_pressed=false;assert(m.play(seq++,1000,h));
 assert(m.tick(2000,h)==0);h.pedal_pressed=true;assert(m.tick(2250,h)==0);
 for(uint64_t t=2500;t<=8022250;t+=250){if(t%100000==0)assert(m.ping(seq++,t));auto mask=m.tick(t,h);assert(m.state!=State::Fault);if(t<222250)assert(mask==0 && m.count[0]==0);}
 assert(m.playback_started_us==222250);assert(m.playback_active);h.pedal_pressed=false;assert(m.tick(8022500,h)==0);assert(!m.playback_active && m.state==State::Armed);
 // Extreme legal knots may overshoot between points; reject before pulses.
 assert(m.load(seq++,8022500,period,n));for(unsigned i=0;i<n;++i)assert(m.knot(seq++,8022500,i,i==1?kMaxCount[0]:0,0));
 m.count=m.knots[0];assert(!m.play(seq,8022500,h));
}
void io_test(){
 CommandInput input;for(int i=0;i<239;++i)assert(input.feed('a')==CommandInput::Result::Pending);assert(input.feed('b')==CommandInput::Result::Invalid);assert(input.feed('\n')==CommandInput::Result::InvalidLine);
 assert(input.feed(0)==CommandInput::Result::Invalid);assert(stop_prefix(" stop anything"));assert(!stop_prefix("st"));
 uint8_t reply[]={5,255,0x6c,0x12,0x34,0x56,0x78,0};reply[7]=tmc_crc(reply,7);TmcReply parser;uint32_t value=0;
 for(unsigned i=0;i<7;++i)assert(!parser.feed(reply[i],0x6c,value));assert(parser.feed(reply[7],0x6c,value));assert(value==0x12345678);
 reply[7]^=1;TmcReply corrupt;for(auto b:reply)assert(!corrupt.feed(b,0x6c,value));
 DriverVerification v;assert(!v.sample_supply(true));auto epoch=v.epoch();assert(v.finish(epoch));assert(v.sample_supply(false));assert(!v.ready());assert(v.sample_supply(true));assert(!v.finish(epoch));assert(v.finish(v.epoch()));
 TickLiveness l;assert(!l.can_feed_watchdog(0));assert(l.can_feed_watchdog(1));assert(!l.can_feed_watchdog(1));
}
int main(){jog_test();independent_faults();trajectory_test();io_test();puts("motion, trajectory, interlocks, framing and UART policy checks passed");}
