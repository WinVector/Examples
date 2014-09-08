package com.mzlabs.count.divideandconquer;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Map;
import java.util.Random;

import org.junit.Test;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.util.IntLinOp;
import com.mzlabs.count.util.IntVec;
import com.mzlabs.count.zeroone.ZeroOneCounter;

public class TestDQ {
	@Test
	public void testDQ() {
		final CountingProblem prob  = new ContingencyTableProblem(3,3);
		final ZeroOneCounter zo = new ZeroOneCounter(prob,false);
		final int[] b = new int[prob.A.length];
		final int[] interior = new int[prob.A[0].length];
		final Random rand = new Random(2426236);
		for(int i=0;i<interior.length;++i) {
			interior[i] = rand.nextInt(3);
		}
		IntLinOp.mult(prob.A,interior,b);
		final BigInteger eoSoln = zo.countNonNegativeSolutions(b);
		final boolean origDebug = DivideAndConquerCounter.debug;
		DivideAndConquerCounter.debug = true;
		for(final boolean allowZONode: new boolean[] { false,true}) {
			final DivideAndConquerCounter dc = new DivideAndConquerCounter(prob,true, false,allowZONode);
			final BigInteger dqSoln = dc.countNonNegativeSolutions(b);
			assertEquals(0,eoSoln.compareTo(dqSoln));
		}
		DivideAndConquerCounter.debug = origDebug;
	}

	@Test
	public void testZO() {
		final CountingProblem prob = new ContingencyTableProblem(4,3);
		final Map<IntVec,BigInteger> z1 = ZeroOneCounter.zeroOneSolutionCounts(prob);
		final Map<IntVec,BigInteger> z2 = DivideAndConquerCounter.zeroOneSolutionCounts(prob);
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
		final int[] b = new int[6];
		Arrays.fill(b,5);
		final BigInteger check = ZeroOneCounter.bruteForceSolnDebug(prob.A, b,false);
		for(final boolean allowZONode: new boolean[] { false,true}) {
			final DivideAndConquerCounter dc = new DivideAndConquerCounter(prob,true, false,allowZONode);
			final BigInteger count = dc.countNonNegativeSolutions(b);
			assertEquals(0,check.compareTo(count));
		}
	}
}
