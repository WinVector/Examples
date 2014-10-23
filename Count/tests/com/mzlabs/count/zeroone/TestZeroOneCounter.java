package com.mzlabs.count.zeroone;

import static org.junit.Assert.assertTrue;

import java.math.BigInteger;
import java.util.Random;

import org.junit.Test;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.op.iter.SeqLT;
import com.mzlabs.count.util.IntLinOp;

public class TestZeroOneCounter {


	@Test
	public void runEx1() {
		final CountingProblem prob = new ContingencyTableProblem(3,2);
		for(final boolean useSDQZO: new boolean[] {true, false}) {
			final ZeroOneCounter cm = new ZeroOneCounter(prob,useSDQZO);
			final SeqLT seq = new SeqLT(prob.A.length,5);
			final int[] b = seq.first();
			BigInteger nRun = BigInteger.ZERO;
			BigInteger nError = BigInteger.ZERO;
			do {
				final BigInteger bruteForceSoln = ZeroOneCounter.bruteForceSolnDebug(prob.A,b,false);
				final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
				if(bruteForceSoln.compareTo(evenOddSoln)!=0) {
					nError = nError.add(BigInteger.ONE);
				}
				nRun = nRun.add(BigInteger.ONE);
			} while(seq.advance(b));
			assertTrue(nError.compareTo(BigInteger.ZERO)==0);
		}
	}

	@Test
	public void runEx2() {
		final CountingProblem prob = new ContingencyTableProblem(3,3);
		for(final boolean useSDQZO: new boolean[] {true, false}) {
			final ZeroOneCounter cm = new ZeroOneCounter(prob,useSDQZO);
			final int[] b = new int[prob.A.length];
			final int[] interior = new int[prob.A[0].length];
			final Random rand = new Random(2426236);
			for(int i=0;i<interior.length;++i) {
				interior[i] = rand.nextInt(3);
			}
			IntLinOp.mult(prob.A,interior,b);
			final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
			final BigInteger bruteForceSoln = ZeroOneCounter.bruteForceSolnDebug(prob.A,b,false);
			final boolean eq = (evenOddSoln.compareTo(bruteForceSoln)==0);
			assertTrue(eq);
		}
	}

	@Test
	public void runEx3() {
		final int m = 3;
		final int n = 3;
		final CountingProblem prob = new ContingencyTableProblem(m,n);
		for(final boolean useSDQZO: new boolean[] {true, false}) {
			final ZeroOneCounter cm = new ZeroOneCounter(prob,useSDQZO);
			final int[] b = new int[prob.A.length];
			final int[] interior = new int[prob.A[0].length];
			final Random rand = new Random(2426236);
			for(int i=0;i<interior.length;++i) {
				interior[i] = rand.nextInt(100);
			}
			IntLinOp.mult(prob.A,interior,b);
			final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
			assertTrue(evenOddSoln.compareTo(BigInteger.ZERO)>0);
		}
	}

}
