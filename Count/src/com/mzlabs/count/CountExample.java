package com.mzlabs.count;

import java.math.BigInteger;
import java.util.Date;
import java.util.Random;

public final class CountExample {
	
	public static boolean runEx1() {
		System.out.println();
		final CountingProblem prob = new ContingencyTableProblem(3,2);
		final CountMat cm = new CountMat(prob);
		final int[] b = new int[prob.A.length];
		BigInteger nRun = BigInteger.ZERO;
		BigInteger nError = BigInteger.ZERO;
		do {
			final BigInteger bruteForceSoln = CountMat.bruteForceSolnDebug(prob.A,b);
			final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
			if(bruteForceSoln.compareTo(evenOddSoln)!=0) {
				System.out.println(new IntVec(b) + "\t" + bruteForceSoln + "\t" + evenOddSoln);
				nError = nError.add(BigInteger.ONE);
			}
			nRun = nRun.add(BigInteger.ONE);
		} while(IntVec.advanceLT(7,b));
		System.out.println(nError + " errors out of " + nRun + " examples");
		System.out.println();
		return nError.compareTo(BigInteger.ZERO)==0;
	}
	
	public static boolean runEx2() {
		System.out.println();
		final CountingProblem prob  = new ContingencyTableProblem(3,3);
		final CountMat cm = new CountMat(prob);
		final int[] b = new int[prob.A.length];
		final int[] interior = new int[prob.A[0].length];
		final Random rand = new Random(2426236);
		for(int i=0;i<interior.length;++i) {
			interior[i] = rand.nextInt(3);
		}
		IntLinOp.mult(prob.A,interior,b);
		System.out.println(new Date());
		final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
		System.out.println(new IntVec(b) + "\teven odd solution\t" + evenOddSoln);
		System.out.println(new Date());
		final BigInteger bruteForceSoln = CountMat.bruteForceSolnDebug(prob.A,b);
		System.out.println(new IntVec(b) + "\tbrute force solution\t" + bruteForceSoln);
		System.out.println(new Date());
		final boolean eq = (evenOddSoln.compareTo(bruteForceSoln)==0);
		System.out.println("equal: " + eq);
		System.out.println();
		return eq;
	}

	public static boolean runEx3() {
		System.out.println();
		final int m = 4;
		final int n = 4;
		final CountingProblem prob = new ContingencyTableProblem(m,n);
		final CountMat cm = new CountMat(prob);
		final int[] b = new int[prob.A.length];
		final int[] interior = new int[prob.A[0].length];
		final Random rand = new Random(2426236);
		for(int i=0;i<interior.length;++i) {
			interior[i] = rand.nextInt(100000);
		}
		IntLinOp.mult(prob.A,interior,b);
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				System.out.print("\t" + "x("+i+","+j+")");
			}
			System.out.println("\t"+b[i]);
		}
		for(int j=0;j<n;++j) {
			System.out.print("\t" + b[j+m]);
		}
		System.out.println();
		System.out.println(new Date());
		final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
		System.out.println(new IntVec(b) + "\teven odd solution\t" + evenOddSoln);
		System.out.println(new Date());
		System.out.println();
		return evenOddSoln.compareTo(BigInteger.ZERO)>0;
	}

	
	public static void main(String[] args) {
		runEx1();
		runEx2();
		runEx3();
	}
}
