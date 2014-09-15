package com.mzlabs.count.op.iter;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import org.junit.Test;

public class TestIters {
	@Test
	public void testSumStepper() {
		final SumStepper stepper = new SumStepper(3,2);
		final int[] x = stepper.first();
		assertEquals(3,x.length);
		int n = 0;
		if(null!=x) {
			do {
				for(final int xi: x) {
					assertTrue((xi>=0)&&(xi<=2));
				}
				++n;
			} while(stepper.advance(x));
		}
		assertEquals(10,n);
	}
}
