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
	
	private final CountingProblem problem;
	private final NonNegativeIntegralCounter underlying;
	
	private static int[][] pickSplitSimple(final int n) {
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
	
	
	
	private final NonNegativeIntegralCounter buildSolnTree(final int[][] Ain, final int[] origVarIndices,
			Map<IntMat,SplitNode> cannonSolns) {
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
		final RowDescription[] rowDescr = IntMat.buildMapToCannon(Ain);
		final int[][] A = IntMat.rowRestrict(Ain,rowDescr);
		// know A is full row rank now
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
			int[][] variableSplit = problem.splitVarsByRef(origVarIndices);
			if(null==variableSplit) {
				// TODO: pick optimal splits
				variableSplit = pickSplitSimple(origVarIndices.length);
			}
			final int[][] subIndices = new int[2][];
			final boolean[][] usesRow = new boolean[2][m];
			final int[][][] Asub = new int[2][][];
			for(int sub=0;sub<2;++sub) {
				final int nSub = variableSplit[sub].length;
				subIndices[sub] = new int[nSub];
				for(int jj=0;jj<nSub;++jj) {
					subIndices[sub][jj] = origVarIndices[variableSplit[sub][jj]];
				}
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
				subsystem[sub] = buildSolnTree(Asub[sub],subIndices[sub],cannonSolns);
			}
			subTree = new SplitNode(A,usesRow,subsystem[0],subsystem[1]);
			cannonSolns.put(matKey,subTree);
		}
		return new RowCannonNode(Ain,rowDescr,subTree);
	}
	
	public DivideAndConquerCounter(final CountingProblem problem) {
		this.problem = problem;
		if(!acceptableA(problem.A)) {
			throw new IllegalArgumentException("non-acceptable A");
		}
		final int n = problem.A[0].length;
		final int[] origVarIndices = new int[n];
		for(int i=0;i<n;++i) {
			origVarIndices[i] = i;
		}
		underlying = buildSolnTree(problem.A,origVarIndices,new HashMap<IntMat,SplitNode>(1000));
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
			System.out.println("" + n + " by " + n + " contingency tables");
			final CountingProblem prob  = new ContingencyTableProblem(n,n);
			System.out.println(new Date());
			final DivideAndConquerCounter dc = new DivideAndConquerCounter(prob);
			System.out.println("dc counter initted");
			System.out.println(new Date());
			final ZeroOneCounter zo;
			if(n<=4) {
				System.out.println("zo counter initted");
				zo = new ZeroOneCounter(prob);
				System.out.println(new Date());
			} else {
				zo = null;
			}
			for(int t=0;t<=1+(n-1)*(n-1);++t) {
				System.out.println();
				final int[] b = new int[prob.A.length];
				Arrays.fill(b,t);
				System.out.println(new Date());
				final BigInteger dqSoln = dc.countNonNegativeSolutions(b);
				System.out.println(new IntVec(b) + "\tdivide and conquer solution\t" + dqSoln);
				System.out.println(new Date());
				if(null!=zo) {
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
