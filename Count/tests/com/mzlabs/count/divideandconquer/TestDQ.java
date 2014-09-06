package com.mzlabs.count.divideandconquer;

import static org.junit.Assert.assertEquals;

import java.math.BigInteger;
import java.util.Random;

import org.junit.Test;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.IntLinOp;
import com.mzlabs.count.ZeroOneCounter;

public class TestDQ {
	@Test
	public void testDQ() {
		final CountingProblem prob  = new ContingencyTableProblem(3,3);
		final boolean origDebug = DivideAndConquerCounter.debug;
		DivideAndConquerCounter.debug = true;
		final DivideAndConquerCounter dc = new DivideAndConquerCounter(prob.A);
		final ZeroOneCounter zo = new ZeroOneCounter(prob);
		final int[] b = new int[prob.A.length];
		final int[] interior = new int[prob.A[0].length];
		final Random rand = new Random(2426236);
		for(int i=0;i<interior.length;++i) {
			interior[i] = rand.nextInt(3);
		}
		IntLinOp.mult(prob.A,interior,b);
		final BigInteger dqSoln = dc.countNonNegativeSolutions(b);
		final BigInteger eoSoln = zo.countNonNegativeSolutions(b);
		DivideAndConquerCounter.debug = origDebug;
		assertEquals(0,eoSoln.compareTo(dqSoln));
	}

}
