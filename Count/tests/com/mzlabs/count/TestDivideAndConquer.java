package com.mzlabs.count;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Map;

import org.junit.Test;

public class TestDivideAndConquer {
	@Test
	public void testZO() {
		final CountingProblem prob = new ContingencyTableProblem(4,3);
		final Map<IntVec,BigInteger> z1 = CountMat.zeroOneSolutionCounts(prob.A);
		final Map<IntVec,BigInteger> z2 = DivideAndConquer.zeroOneSolutionCounts(prob.A);
		assertEquals(z1.size(),z2.size());
		for(final Map.Entry<IntVec,BigInteger> me: z1.entrySet()) {
			final IntVec b = me.getKey();
			final BigInteger c1 = me.getValue();
			final BigInteger c2 = z2.get(b);
			assertNotNull(c2);
			assertEquals(0,c1.compareTo(c2));
		}
	}
	
	@Test
	public void testInt() {
		final CountingProblem prob = new ContingencyTableProblem(3,3);
		final DivideAndConquer dc = new DivideAndConquer(prob.A,false);
		final int[] b = new int[6];
		Arrays.fill(b,5);
		final BigInteger count = dc.solutionCount(b);
		final BigInteger check = CountMat.bruteForceSolnDebug(prob.A, b);
		assertEquals(0,check.compareTo(count));
	}
}
