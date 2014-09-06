package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;
import java.util.Date;
import java.util.Random;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.IntLinOp;
import com.mzlabs.count.IntVec;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.ZeroOneCounter;

public final class DivideAndConquerCounter implements NonNegativeIntegralCounter {

	private static boolean acceptableA(final int[][] A) {
		final int m = A.length;
		if(m<1) {
			return false;
		}
		final int n = A[0].length;
		if(n<1) {
			return false;
		}
		for(int j=0;j<n;++j) {
			boolean sawNZ = false;
			for(int i=0;i<m;++i) {
				if((A[i][j]<0)||(A[i][j]>1)) {
					return false;
				}
				if(A[i][j]>0) {
					sawNZ = true;
				}
			}
			if(!sawNZ) {
				return false;
			}
		}
		return true;
	}
	
	private final NonNegativeIntegralCounter underlying;
	
	private static final NonNegativeIntegralCounter buildSolnTree(final int[][] A) {
		final TerminalNode nd = TerminalNode.tryToBuildTerminalNode(A);
		if(null!=nd) {
			return nd;
		}
		final int n = A[0].length;
		final int m = A.length;
		if(n<=1) {
			throw new IllegalStateException("terminal case didn't catch single column case");
		}
		// TODO: don't copy out zeroed rows
		final int n1 = n/2;
		final int n2 = n - n1;
		final int[][] A1 = new int[m][n1];
		final int[][] A2 = new int[m][n2];
		for(int i=0;i<m;++i) {
			for(int j=0;j<n1;++j) {
				A1[i][j] = A[i][j];
			}
			for(int j=0;j<n2;++j) {
				A2[i][j] = A[i][n1+j];
			}
		}
		final NonNegativeIntegralCounter leftSubsystem = buildSolnTree(A1);
		final NonNegativeIntegralCounter rightSubsystem = buildSolnTree(A2);
		return new SplitNode(A,leftSubsystem,rightSubsystem);
	}
	
	public DivideAndConquerCounter(final int[][] A) {
		if(!acceptableA(A)) {
			throw new IllegalArgumentException("non-acceptable A");
		}
		underlying = buildSolnTree(A);
	}
	

	@Override
	public BigInteger countNonNegativeSolutions(final int[] b) {
		return underlying.countNonNegativeSolutions(b);
	}
	
	@Override
	public String toString() {
		return "dq(" + underlying + ")";
	}
	
	public static void main(final String[] args) {
		System.out.println();
		final CountingProblem prob  = new ContingencyTableProblem(3,3);
		final DivideAndConquerCounter dc = new DivideAndConquerCounter(prob.A);
		final int[] b = new int[prob.A.length];
		final int[] interior = new int[prob.A[0].length];
		final Random rand = new Random(2426236);
		for(int i=0;i<interior.length;++i) {
			interior[i] = rand.nextInt(3);
		}
		IntLinOp.mult(prob.A,interior,b);
		System.out.println(new Date());
		final BigInteger evenOddSoln = dc.countNonNegativeSolutions(b);
		System.out.println(new IntVec(b) + "\tdivide and conquer solution\t" + evenOddSoln);
		System.out.println(new Date());
		final BigInteger bruteForceSoln = ZeroOneCounter.bruteForceSolnDebug(prob.A,b);
		System.out.println(new IntVec(b) + "\tbrute force solution\t" + bruteForceSoln);
		System.out.println(new Date());
		final boolean eq = (evenOddSoln.compareTo(bruteForceSoln)==0);
		System.out.println("equal: " + eq);
		System.out.println();
	}

}
