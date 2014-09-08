package com.mzlabs.count;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Date;
import java.util.Random;

import com.mzlabs.count.util.IntLinOp;
import com.mzlabs.count.util.IntVec;
import com.mzlabs.count.zeroone.ZeroOneCounter;

public final class CountExample {
	
	public static boolean runEx1() {
		System.out.println();
		final CountingProblem prob = new ContingencyTableProblem(3,2);
		final ZeroOneCounter cm = new ZeroOneCounter(prob,false);
		final int[] b = new int[prob.A.length];
		BigInteger nRun = BigInteger.ZERO;
		BigInteger nError = BigInteger.ZERO;
		do {
			final BigInteger bruteForceSoln = ZeroOneCounter.bruteForceSolnDebug(prob.A,b,false);
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
		final ZeroOneCounter cm = new ZeroOneCounter(prob,false);
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
		final BigInteger bruteForceSoln = ZeroOneCounter.bruteForceSolnDebug(prob.A,b,false);
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
		final ZeroOneCounter zo = new ZeroOneCounter(prob,false);
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
		final BigInteger evenOddSoln = zo.countNonNegativeSolutions(b);
		System.out.println(new IntVec(b) + "\teven odd solution\t" + evenOddSoln);
		System.out.println(new Date());
		System.out.println();
		return evenOddSoln.compareTo(BigInteger.ZERO)>0;
	}
	
	static double evalPoly(final BigInteger[] ys, final double x) {
		final int k = ys.length;
		double sum = 0.0;
		for(int i=0;i<k;++i) {
			double prod = 1.0;
			for(int j=0;j<k;++j) {
				if(j!=i) {
					final double term = (x-j)/(double)(i-j);
					prod *= term;
				}
			}
			sum += ys[i].doubleValue()*prod;
		}
		return sum;
	}
	
	public static void runEx4(final int n) {
		System.out.println();
		System.out.println(new Date());
		final CountingProblem prob = new ContingencyTableProblem(n,n);
		final ZeroOneCounter cm = new ZeroOneCounter(prob,false);
		System.out.println("have counter zero/one structures");
		System.out.println(new Date());
		final int[] b = new int[prob.A.length];
		final BigInteger[] ys = new BigInteger[(n-1)*(n-1)+1];
		for(int i= 0;i<ys.length;++i) {
			Arrays.fill(b,i);
			ys[i] = cm.countNonNegativeSolutions(b);
			System.out.println("evenOdd(" + n + "," + n + ";" + i +")= " + ys[i]);
			System.out.println(new Date());
		}
		for(int i=0;i<=2*n*n;++i) {
			Arrays.fill(b,i);
			final double polyEval = evalPoly(ys,i);
			System.out.println("\tpoly(" + n + "," + n + ";" + i +")= " + polyEval);
		}
		System.out.println(new Date());
		System.out.println();
	}

	
	public static void main(String[] args) {
		runEx1();
		runEx2();
		runEx3();
		for(int n=1;n<=5;++n) {
			runEx4(n);
		}
	}
}
