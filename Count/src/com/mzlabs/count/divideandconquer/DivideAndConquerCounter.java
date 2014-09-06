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
	static boolean debug = true;

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
		// TODO: pick optimal splits
		final int[][] variableSplit = new int[2][];
		variableSplit[0] = new int[n/2];
		variableSplit[1] = new int[n-n/2];
		for(int j=0;j<variableSplit[0].length;++j) {
			variableSplit[0][j] = j;
		}
		for(int j=0;j<variableSplit[1].length;++j) {
			variableSplit[1][j] = variableSplit[0].length + j;
		}
		final boolean[][] usesRow = new boolean[2][m];
		final int[][][] Asub = new int[2][][];
		for(int sub=0;sub<2;++sub) {
			Asub[sub] = IntVec.colRestrict(A,variableSplit[sub]);
			for(int i=0;i<m;++i) {
				for(final int j: variableSplit[sub]) {
					if(A[i][j]!=0) {
						usesRow[sub][i] = true;
					}
				}
			}
		}
		final NonNegativeIntegralCounter[] subsystem = new NonNegativeIntegralCounter[2];
		for(int sub=0;sub<2;++sub) {
			final int[] nzRows = IntVec.nonZeroRows(Asub[sub]);
			if(nzRows.length<m) {
				final int[][] Adrop = IntVec.rowRestrict(Asub[sub],nzRows);
				subsystem[sub] = new RowDropNode(Asub[sub],nzRows,buildSolnTree(Adrop));
			} else {
				subsystem[sub] = buildSolnTree(Asub[sub]);
			}
		}
		return new SplitNode(A,usesRow,subsystem[0],subsystem[1]);
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
		final ZeroOneCounter zo = new ZeroOneCounter(prob,false);
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
		final BigInteger bruteForceSoln = zo.countNonNegativeSolutions(b);
		System.out.println(new IntVec(b) + "\tzero one solution\t" + bruteForceSoln);
		System.out.println(new Date());
		final boolean eq = (evenOddSoln.compareTo(bruteForceSoln)==0);
		System.out.println("equal: " + eq);
		System.out.println();
	}

}
