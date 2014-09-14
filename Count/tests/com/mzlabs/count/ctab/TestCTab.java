package com.mzlabs.count.ctab;

import static org.junit.Assert.*;

import java.math.BigInteger;

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
	
	@Test
	public void testCounter() {
		for(int rowsCols=1;rowsCols<=4;++rowsCols) {
			final CTab ctab = new CTab(rowsCols);
			for(int total=0;total<=10;++total) {
				final BigInteger count = ctab.countSqTables(rowsCols,total); 
				final BigInteger check = ctab.debugConfirmSqTables(rowsCols, total);
				final boolean eq = (check.compareTo(count)==0);
				assertTrue(eq);
				//System.out.println(rowsCols + "\t" + total + "\t" + count + "\t" + check + "\t" + eq);
			}
		}
	}
}
