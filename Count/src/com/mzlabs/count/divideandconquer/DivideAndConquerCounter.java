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
	static boolean allowParallel = true;
	private final CountingProblem problem;
	private final NonNegativeIntegralCounter underlying;
	private final boolean zeroOne;
	
	public DivideAndConquerCounter(final CountingProblem problem, final boolean zeroOne) {
		this.problem = problem;
		this.zeroOne = zeroOne;
		if(!acceptableA(problem.A)) {
			throw new IllegalArgumentException("non-acceptable A");
		}
		final int n = problem.A[0].length;
		final int[] origVarIndices = new int[n];
		for(int i=0;i<n;++i) {
			origVarIndices[i] = i;
		}
		underlying = buildSolnTree(problem.A,origVarIndices,new HashMap<IntMat,SplitNode>(1000),allowParallel);
	}
	

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
			final Map<IntMat,SplitNode> cannonSolns, final boolean runParrallel) {
		if(Ain.length<1) {
			throw new IllegalArgumentException("called on zero-row system");
		}
		if(Ain[0].length<1) {
			throw new IllegalArgumentException("called on zero-column system");
		}
		{   // see we have a terminal case (full column rank sub-systems)
			final TerminalNode nd = TerminalNode.tryToBuildTerminalNode(Ain,zeroOne);
			if(null!=nd) {
				return nd;
			}
		}
		// Canonicalize matrix rows
		final RowDescription[] rowDescr = IntMat.buildMapToCannon(Ain);
		final int[][] A = IntMat.rowRestrict(Ain,rowDescr);
		// know A is full row rank now
		{   // check again if we have a terminal case (full column rank sub-systems)
			final TerminalNode nd = TerminalNode.tryToBuildTerminalNode(Ain,zeroOne);
			if(null!=nd) {
				return new RowCannonNode(Ain,rowDescr,nd,zeroOne);
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
				// TODO: pick optimal splits in this case
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
				subsystem[sub] = buildSolnTree(Asub[sub],subIndices[sub],cannonSolns,false);
			}
			subTree = new SplitNode(A,usesRow,runParrallel,subsystem[0],subsystem[1],zeroOne);
			cannonSolns.put(matKey,subTree);
		}
		return new RowCannonNode(Ain,rowDescr,subTree,zeroOne);
	}
	


	@Override
	public BigInteger countNonNegativeSolutions(final int[] bIn) {
		for(final int bi: bIn) {
			if(bi<0) {
				throw new IllegalArgumentException("negative b entry");
			}
		}
		if(!problem.admissableB(bIn)) {
			return BigInteger.ZERO;
		}
		final IntVec bNormal = problem.normalForm(bIn);
		return underlying.countNonNegativeSolutions(bNormal.asVec());
	}
	
	@Override
	public String toString() {
		return "dq(" + underlying + ")";
	}
	
	/**
	 * 
	 * @return map from every b such that problem.A z = b is solvable for z zero/one to how many such z there are
	 */
	public static Map<IntVec,BigInteger> zeroOneSolutionCounts(final CountingProblem problem) {
		final DivideAndConquerCounter dc = new DivideAndConquerCounter(problem,true);
		final Map<IntVec,BigInteger> solnCounts = new HashMap<IntVec,BigInteger>();
		final int m = problem.A.length;
		final int n = problem.A[0].length;
		final int[] bounds = new int[m];
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				bounds[i] += problem.A[i][j];
			}
		}
		final IntVec boundsVec = new IntVec(bounds);
		final int[] b = new int[m];
		do {
			final BigInteger nsolns = dc.countNonNegativeSolutions(b);
			if(nsolns.compareTo(BigInteger.ZERO)>0) {
				solnCounts.put(new IntVec(b),nsolns);
			}
		} while(boundsVec.advanceLE(b));
//		System.out.println("dc cache size: " + dc.cache.size());
//		System.out.println("dc result size: " + solnCounts.size());
//		BigInteger total = BigInteger.ZERO;
//		for(final BigInteger ci: solnCounts.values()) {
//			total = total.add(ci);
//		}
//		System.out.println("dc total solns: " + total);
//		System.out.println("dc m,n,2^n: " + m + " " + n + " " + Math.pow(2,n));
//		System.out.println("base cases");
//		for(final Entry<IntVec, LinOpCarrier<JBlasMatrix>> me: dc.inverseOp.entrySet()) {
//			if(me.getValue().inv!=null) {
//				System.out.println("\t" + me.getKey());
//			}
//		}
		return solnCounts;
	}
	
	
	public static void main(final String[] args) {
		System.out.println();
		for(int n=1;n<=9;++n) {
			System.out.println();
			System.out.println("" + n + " by " + n + " contingency tables");
			final CountingProblem prob  = new ContingencyTableProblem(n,n);
			System.out.println(new Date());
			final DivideAndConquerCounter dc = new DivideAndConquerCounter(prob,false);
			System.out.println("dc counter initted");
			System.out.println("\t" + dc);
			System.out.println(new Date());
			final ZeroOneCounter zo;
			if(n<=4) {
				System.out.println("zo counter initted");
				zo = new ZeroOneCounter(prob,true);
				System.out.println(new Date());
			} else {
				zo = null;
			}
			for(int t=0;t<=(n*n-3*n+2)/2;++t) {
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