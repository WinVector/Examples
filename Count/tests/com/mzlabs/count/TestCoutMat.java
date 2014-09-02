package com.mzlabs.count;

import static org.junit.Assert.assertTrue;

import java.math.BigInteger;
import java.util.Random;

import org.junit.Test;

public class TestCoutMat {

	
	@Test
	public void runEx1() {
		final int[][] A = CountExample.contingencyTable(3,2);
		final CountMat cm = new CountMat(A);
		final int[] b = new int[A.length];
		BigInteger nRun = BigInteger.ZERO;
		BigInteger nError = BigInteger.ZERO;
		do {
			final BigInteger bruteForceSoln = CountMat.bruteForceSolnDebug(A,b);
			final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
			if(bruteForceSoln.compareTo(evenOddSoln)!=0) {
				nError = nError.add(BigInteger.ONE);
			}
			nRun = nRun.add(BigInteger.ONE);
		} while(IntVec.advanceLT(5,b));
		assertTrue(nError.compareTo(BigInteger.ZERO)==0);
	}
	
	@Test
	public void runEx2() {
		final int[][] A = CountExample.contingencyTable(3,3);
		final CountMat cm = new CountMat(A);
		final int[] b = new int[A.length];
		final int[] interior = new int[A[0].length];
		final Random rand = new Random(2426236);
		for(int i=0;i<interior.length;++i) {
			interior[i] = rand.nextInt(3);
		}
		IntLinOp.mult(A,interior,b);
		final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
		final BigInteger bruteForceSoln = CountMat.bruteForceSolnDebug(A,b);
		final boolean eq = (evenOddSoln.compareTo(bruteForceSoln)==0);
		assertTrue(eq);
	}

	@Test
	public void runEx3() {
		final int m = 3;
		final int n = 3;
		final int[][] A = CountExample.contingencyTable(m,n);
		final CountMat cm = new CountMat(A);
		final int[] b = new int[A.length];
		final int[] interior = new int[A[0].length];
		final Random rand = new Random(2426236);
		for(int i=0;i<interior.length;++i) {
			interior[i] = rand.nextInt(1000);
		}
		IntLinOp.mult(A,interior,b);
		final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
		assertTrue(evenOddSoln.compareTo(BigInteger.ZERO)>0);
	}

}
