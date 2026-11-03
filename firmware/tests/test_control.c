#include <assert.h>
#include <stdio.h>
#include "proto_control.h"

/* Synthetic engineering thresholds exercise logic; these are not product limits. */
static const r0_limits_t limits = {true, 25, 50000, 3000, 3000, 60000, 2500};
static r0_inputs_t healthy(uint64_t now) {
    return (r0_inputs_t){.docked=false,.sensors_valid=true,.sampled_ms=now,
                        .temperature_millic=25000,.battery_mv=3800};
}
static r0_control_t ready(uint64_t now) {
    r0_control_t c; r0_control_init(&c, limits);
    r0_control_tick(&c, healthy(now), now);
    return c;
}
int main(void) {
    r0_control_t c = ready(100);
    assert(c.output_percent==0 && !c.armed);
    assert(!r0_request_motor(&c,25,100));
    assert(r0_local_arm(&c,100));
    assert(!r0_request_motor(&c,26,100));
    assert(r0_request_motor(&c,25,100));
    assert(c.output_percent==25);
    r0_control_tick(&c,healthy(3099),3099); assert(c.output_percent==25);
    r0_control_tick(&c,healthy(3100),3100); assert(c.output_percent==0);
    assert(r0_request_motor(&c,10,3101));
    r0_inputs_t in=healthy(3102); in.docked=true;
    r0_control_tick(&c,in,3102); assert(!c.armed && c.output_percent==0);
    r0_control_tick(&c,healthy(3103),3103); assert(!c.armed && c.output_percent==0);
    assert(r0_local_arm(&c,4000)); assert(r0_request_motor(&c,20,4000));
    in=healthy(4001); in.sensors_valid=false;
    r0_control_tick(&c,in,4001); assert(c.faults & R0_FAULT_SENSOR); assert(!c.armed);
    r0_control_tick(&c,healthy(4002),4002); assert(c.faults); assert(!r0_local_arm(&c,4002));
    assert(r0_local_clear(&c,4002)); assert(!c.armed);
    assert(r0_local_arm(&c,4002)); assert(r0_request_motor(&c,20,4002));
    in=healthy(4003); in.temperature_millic=50000;
    r0_control_tick(&c,in,4003); assert(c.faults & R0_FAULT_TEMPERATURE); assert(c.output_percent==0);
    assert(!r0_local_clear(&c,4003));
    c=ready(10); in=healthy(10); r0_control_tick(&c,in,2511);
    assert(c.faults & R0_FAULT_SENSOR);
    c=ready(10); in=healthy(11); in.battery_mv=2999;
    r0_control_tick(&c,in,11); assert(c.faults & R0_FAULT_BATTERY);
    c=ready(10); assert(r0_local_arm(&c,10));
    assert(!r0_request_motor(&c,10,60010));
    c=ready(10); c.limits.temperature_trip_millic=0; assert(!r0_limits_ready(&c)); assert(!r0_local_arm(&c,10));
    c=ready(10); c.limits.motor_enabled=false; assert(!r0_local_arm(&c,10));
    c=ready(10); c.faults=R0_FAULT_HARDWARE; assert(!r0_local_clear(&c,10));
    c=ready(10); assert(r0_local_arm(&c,10)); assert(r0_request_motor(&c,25,10));
    r0_stop(&c); assert(!c.armed && !c.output_percent); assert(!r0_request_motor(&c,25,11));
    const uint8_t t1[]={0x12,0xc0}, t2[]={0xff,0xf8}, t3[]={0xf3,0x80};
    assert(r0_decode_temperature(t1)==37500); assert(r0_decode_temperature(t2)==-62);
    assert(r0_decode_temperature(t3)==-25000);
    const uint8_t t4[]={0xe4,0x80}, t5[]={0x4b,0x00}, startup[]={0x80,0x00};
    assert(r0_decode_temperature(t4)==-55000); assert(r0_decode_temperature(t5)==150000);
    assert(r0_decode_temperature(startup)==-256000);
    const uint8_t a[]={0x00,0xfc}; assert(r0_decode_axis(a)==-1024);
    puts("PASS: boot/off, local-arm gate, duty bounds, lease expiry, dock removal, sensor fault latch, temperature/battery trips, stale sensor, arm timeout, default/config lock, hardware latch, stop and signed sensor decoding");
    return 0;
}
