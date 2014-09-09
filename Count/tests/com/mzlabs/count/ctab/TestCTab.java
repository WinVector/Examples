package com.mzlabs.count.ctab;

import static org.junit.Assert.*;

import org.junit.Test;

public class TestCTab {
	@Test
	public void testStepper() {
		for(int dim=1;dim<=4;++dim) {
			for(int bound=0;bound<=5;++bound) {
				assertTrue(new OrderStepper(dim,bound).checks());
			}
		}
	}

}
