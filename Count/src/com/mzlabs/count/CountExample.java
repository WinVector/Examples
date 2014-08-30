package com.mzlabs.count;

import java.math.BigInteger;
import java.util.Date;
import java.util.Random;

public final class CountExample {

	public static int[][] contingencyTable(final int a, final int b) {
		final int m = a+b;
		final int n = a*b;
		final int[][] A = new int[m][n];
		for(int i=0;i<a;++i) {
			for(int j=0;j<b;++j) {
				final int cell = i*b+j;
				A[i][cell] = 1;
				A[j+a][cell] = 1;
			}
		}
		return A;
	}
	
	public static boolean runEx1() {
		System.out.println();
		final int[][] A = contingencyTable(3,2);
		final CountMat cm = new CountMat(A);
		final int[] b = new int[A.length];
		BigInteger nRun = BigInteger.ZERO;
		BigInteger nError = BigInteger.ZERO;
		do {
			final BigInteger bruteForceSoln = CountMat.bruteForceSolnDebug(A,b);
			final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
			if(bruteForceSoln.compareTo(evenOddSoln)!=0) {
				System.out.println(new IntVec(b) + "\t" + bruteForceSoln + "\t" + evenOddSoln);
				nError = nError.add(BigInteger.ONE);
			}
			nRun = nRun.add(BigInteger.ONE);
		} while(CountMat.advance(7,b));
		System.out.println(nError + " errors out of " + nRun + " examples");
		System.out.println();
		return nError.compareTo(BigInteger.ZERO)==0;
	}
	
	public static boolean runEx2() {
		System.out.println();
		final int[][] A = contingencyTable(3,3);
		final CountMat cm = new CountMat(A);
		final int[] b = new int[A.length];
		final int[] interior = new int[A[0].length];
		final Random rand = new Random(2426236);
		for(int i=0;i<interior.length;++i) {
			interior[i] = rand.nextInt(3);
		}
		IntLinOp.mult(A,interior,b);
		System.out.println(new Date());
		final BigInteger evenOddSoln = cm.countNonNegativeSolutions(b);
		System.out.println(new IntVec(b) + "\teven odd solution\t" + evenOddSoln);
		System.out.println(new Date());
		final BigInteger bruteForceSoln = CountMat.bruteForceSolnDebug(A,b);
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
		final int[][] A = contingencyTable(m,n);
		final CountMat cm = new CountMat(A);
		final int[] b = new int[A.length];
		final int[] interior = new int[A[0].length];
		final Random rand = new Random(2426236);
		for(int i=0;i<interior.length;++i) {
			interior[i] = rand.nextInt(100000);
		}
		IntLinOp.mult(A,interior,b);
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
