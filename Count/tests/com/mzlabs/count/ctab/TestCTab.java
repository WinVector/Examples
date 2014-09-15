package com.mzlabs.count.ctab;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

import java.math.BigInteger;

import org.junit.Test;

import com.mzlabs.count.op.iter.OrderStepper;

public class TestCTab {
	@Test
	public void testStepper() {
		for(int dim=1;dim<=4;++dim) {
			for(int bound=0;bound<=5;++bound) {
				final OrderStepper orderStepper = new OrderStepper(dim,bound,-1);
				final boolean eq = orderStepper.checks();
				assertTrue(eq);
			}
		}
	}
	
	@Test
	public void testCounter() {
		for(int rowsCols=1;rowsCols<=4;++rowsCols) {
			final CTab ctab = new CTab(rowsCols,true);
			for(int total=0;total<=10;++total) {
				final BigInteger count = ctab.countSqTables(rowsCols,total); 
				final BigInteger check = ctab.debugConfirmSqTables(rowsCols, total);
				final boolean eq = (check.compareTo(count)==0);
				assertTrue(eq);
				//System.out.println(rowsCols + "\t" + total + "\t" + count + "\t" + check + "\t" + eq);
			}
		}
	}

	@Test
	public void advanceBug2a() {
		final int rowsCols = 3;
		final int total = 5;
		final CTab ctab = new CTab(rowsCols,false);
		final BigInteger count = ctab.countSqTables(rowsCols,total); 
		final BigInteger check = ctab.debugConfirmSqTables(rowsCols, total);
		final boolean eq = (check.compareTo(count)==0);
		assertTrue(eq);
		//System.out.println(rowsCols + "\t" + total + "\t" + count + "\t" + check + "\t" + eq);
	}
	
	@Test
	public void advanceBug2b() {
		final OrderStepper stepper = new OrderStepper(2,5,3);
		final int[] x = stepper.first();
		int n = 0;
		do {
			//System.out.println(IntVec.toString(x));
			++n;
		} while(stepper.advance(x));
		assertEquals(2,n);
	}
	
	@Test
	public void advanceBug1() {
		final OrderStepper stepper = new OrderStepper(1,4,2);
		final int[] x = stepper.first();
		do {
			assertEquals(2,x[0]);
		} while(stepper.advance(x));
	}
}
