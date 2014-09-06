package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.IntVec;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.ZeroOneCounter;
import com.mzlabs.count.divideandconquer.IntMat.RowDescription;

public final class DivideAndConquerCounter implements NonNegativeIntegralCounter {
	static boolean debug = false;

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
	
	private static int[][] pickSplitSimple(final int[][] A) {
		final int n = A[0].length;
		final int[][] variableSplit = new int[2][];
		variableSplit[0] = new int[n/2];
		variableSplit[1] = new int[n-n/2];
		for(int j=0;j<variableSplit[0].length;++j) {
			variableSplit[0][j] = j;
		}
		for(int j=0;j<variableSplit[1].length;++j) {
			variableSplit[1][j] = variableSplit[0].length + j;
		}
		return variableSplit;
	}
	
	private static final NonNegativeIntegralCounter buildSolnTree(final int[][] Ain, Map<IntMat,SplitNode> cannonSolns) {
		if(Ain.length<1) {
			throw new IllegalArgumentException("called on zero-row system");
		}
		if(Ain[0].length<1) {
			throw new IllegalArgumentException("called on zero-column system");
		}
		{   // see we have a terminal case (full column rank sub-systems)
			final TerminalNode nd = TerminalNode.tryToBuildTerminalNode(Ain);
			if(null!=nd) {
				return nd;
			}
		}
		// Canonicalize matrix rows
		final RowDescription[] rowDescr = IntMat.buildMapToCannon(Ain,false);
		final int[][] A = IntMat.rowRestrict(Ain,rowDescr);
		{   // check again if we have a terminal case (full column rank sub-systems)
			final TerminalNode nd = TerminalNode.tryToBuildTerminalNode(Ain);
			if(null!=nd) {
				return new RowCannonNode(Ain,rowDescr,nd);
			}
		}
		final IntMat matKey = new IntMat(A);
		SplitNode subTree = cannonSolns.get(matKey);
		if(null==subTree) {
			final int m = A.length;
			final int n = A[0].length;
			if(n<=1) {
				throw new IllegalStateException("terminal case didn't catch single column case");
			}
			// TODO: pick optimal splits
			final int[][] variableSplit = pickSplitSimple(A);
			final boolean[][] usesRow = new boolean[2][m];
			final int[][][] Asub = new int[2][][];
			for(int sub=0;sub<2;++sub) {
				Asub[sub] = IntMat.colRestrict(A,variableSplit[sub]);
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
				subsystem[sub] = buildSolnTree(Asub[sub],cannonSolns);
			}
			subTree = new SplitNode(A,usesRow,subsystem[0],subsystem[1]);
			cannonSolns.put(matKey,subTree);
		}
		return new RowCannonNode(Ain,rowDescr,subTree);
	}
	
	public DivideAndConquerCounter(final int[][] A) {
		if(!acceptableA(A)) {
			throw new IllegalArgumentException("non-acceptable A");
		}
		underlying = buildSolnTree(A,new HashMap<IntMat,SplitNode>(1000));
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
		for(int n=1;n<=10;++n) {
			System.out.println();
			for(int t=0;t<=1+(n-1)*(n-1);++t) {
				System.out.println();
				System.out.println("" + n + " by " + n + " contingency tables with all rows/columns summing to " + t);
				final CountingProblem prob  = new ContingencyTableProblem(n,n);
				final DivideAndConquerCounter dc = new DivideAndConquerCounter(prob.A);
				final int[] b = new int[prob.A.length];
				Arrays.fill(b,t);
				System.out.println(new Date());
				final BigInteger dqSoln = dc.countNonNegativeSolutions(b);
				System.out.println(new IntVec(b) + "\tdivide and conquer solution\t" + dqSoln);
				System.out.println(new Date());
				if(n<=4) {
					final ZeroOneCounter zo = new ZeroOneCounter(prob);
					final BigInteger eoSoln = zo.countNonNegativeSolutions(b);
					System.out.println(new IntVec(b) + "\tzero one solution\t" + eoSoln);
					System.out.println(new Date());
					final boolean eq = (dqSoln.compareTo(eoSoln)==0);
					System.out.println("equal: " + eq);
					System.out.println();
					if(!eq) {
						throw new IllegalStateException("answers did not match");
					}
				}
			}
		}
	}

}
