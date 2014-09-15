package com.mzlabs.count.Minkowski;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

import com.mzlabs.count.op.iter.SetStepper;

public final class TestSetStepper {
	@Test
	public void testStepper() {
		final int m = 3;
		final int n = 5;
		final SetStepper setStepper = new SetStepper(m,n);
		final int[] x = setStepper.first();
		int nSaw = 0;
		do {
			++nSaw;
		} while(setStepper.advance(x));
		assertEquals(10,nSaw);  // nSaw should be (n choose m)
	}

}
