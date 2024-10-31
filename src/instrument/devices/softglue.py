from ophyd import Component, Device, EpicsSignal


class SoftGlue(Device):

    acq_period = Component(EpicsSignal, "8idi:SGControl1.A", kind="config")
    acq_time = Component(EpicsSignal, "8idi:SGControl1.C", kind="config")
    num_triggers = Component(EpicsSignal, "8idi:SGControl1.J", kind="config")
    stop_trigger = Component(EpicsSignal, "8idi:softGlueA:OR-1_IN2_Signal", kind="config")

    # avoid the name 'trigger' since Device has a '.trigger()' method.
    sg_trigger = Component(
        EpicsSignal,
        "8idi:softGlueA:MUX2-1_IN0_Signal",
        kind="omitted",
        string=True,
        trigger_value="1!",
    )

    sg_stop_trigger = Component(
        EpicsSignal,
        "8idi:softGlueA:OR-1_IN2_Signal",
        kind="omitted",
        string=True,
    )

    def stop(self, *, success=False):
        self.sg_stop_trigger.put("1!")
        super().stop(success=success)

    # FIXME upstream : This code uses self.trigger_value
    # https://github.com/aps-8id-dys/bluesky/issues/99
    def trigger(self):
        """BUGFIX - Put the acq_signal's 'trigger_value' instead of 1."""
        from ophyd.status import DeviceStatus

        signals = self.trigger_signals
        if len(signals) > 1:
            raise NotImplementedError(
                "More than one trigger signal is not currently supported."
            )
        status = DeviceStatus(self)
        if not signals:
            status.set_finished()
            return status

        (acq_signal,) = signals

        self.subscribe(status._finished, event_type=self.SUB_ACQ_DONE, run=False)

        def done_acquisition(**ignored_kwargs):
            # Keyword arguments are ignored here from the EpicsSignal
            # subscription, as the important part is that the put completion
            # has finished
            self._done_acquiring()

        # acq_signal.put(1, wait=False, callback=done_acquisition)  # ORIGINAL
        trigger_value = self._sig_attrs[acq_signal.attr_name].trigger_value
        acq_signal.put(trigger_value, wait=False, callback=done_acquisition)
        return status


softglue_8idi = SoftGlue("", name="softglue_8idi")
