package com.mzlabs.count.divideandconquer;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

import com.mzlabs.count.ContingencyTableProblem;
import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.op.IntFunc;
import com.mzlabs.count.op.Reducer;
import com.mzlabs.count.op.Sequencer;
import com.mzlabs.count.op.impl.SimpleSum;
import com.mzlabs.count.op.impl.ThreadedSum;
import com.mzlabs.count.op.iter.RangeIter;
import com.mzlabs.count.op.iter.SeqLE;
import com.mzlabs.count.util.IntMat;
import com.mzlabs.count.util.IntMat.RowDescription;
import com.mzlabs.count.util.IntVec;
import com.mzlabs.count.util.Permutation;
import com.mzlabs.count.zeroone.ZeroOneCounter;
import com.mzlabs.count.zeroone.ZeroOneStore;

public final class DivideAndConquerCounter implements NonNegativeIntegralCounter {
	static boolean debug = false;
	private final CountingProblem problem;
	private final NonNegativeIntegralCounter underlying;
	private final boolean zeroOne;
	private final boolean allowZeroOneNode;
	
	public DivideAndConquerCounter(final CountingProblem problem, boolean allowParallel, final boolean zeroOne, final boolean allowZeroOneNode) {
		this.problem = problem;
		this.zeroOne = zeroOne;
		this.allowZeroOneNode = allowZeroOneNode && (!zeroOne);
		if(!acceptableA(problem.A)) {
			throw new IllegalArgumentException("non-acceptable A");
		}
		final int n = problem.A[0].length;
		final int[] origVarIndices = new int[n];
		for(int i=0;i<n;++i) {
			origVarIndices[i] = i;
		}
		underlying = buildSolnTree(problem.A,origVarIndices,new HashMap<IntMat,NonNegativeIntegralCounter>(1000),allowParallel);
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
			final Map<IntMat,NonNegativeIntegralCounter> cannonSolns, final boolean runParrallel) {
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
		// Canonicalize matrix rows and ensure full row-rank
		final RowDescription[] rowDescr = IntMat.buildMapToCannon(Ain);
		final int[][] A = IntMat.rowRestrict(Ain,rowDescr);
		// know A is full row rank now
		{   // check again if we have a terminal case (full column rank sub-systems)
			final TerminalNode nd = TerminalNode.tryToBuildTerminalNode(A,zeroOne);
			if(null!=nd) {
				return new RowCannonNode(Ain,rowDescr,nd,zeroOne);
			}
		}
		final IntMat matKey = new IntMat(A);
		NonNegativeIntegralCounter subTree = cannonSolns.get(matKey);
		if(null==subTree) {
			final int m = A.length;
			final int n = A[0].length;
			if(n<=1) {
				throw new IllegalStateException("terminal case didn't catch single column case");
			}
			if((allowZeroOneNode)&&(!zeroOne)&&(n<=28)) {
				final ZeroOneCounter zoc = new ZeroOneCounter(new CountingProblem(A),false);
				subTree = zoc;
			} else {
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
			}
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
		final Permutation perm = problem.toNormalForm(bIn);
		final IntVec bNormal = new IntVec(perm.apply(bIn));
		return underlying.countNonNegativeSolutions(bNormal.asVec());
	}
	
	@Override
	public String toString() {
		return "dc(" + underlying + ")";
	}
	
	@Override
	public boolean obviouslyEmpty(final int[] bIn) {
		return false;
	}
	
	
	
	/**
	 * 
	 * @return map from every b such that problem.A z = b is solvable for z zero/one to how many such z there are
	 */
	public static Map<IntVec,BigInteger> zeroOneSolutionCounts(final CountingProblem problem) {
		final int m = problem.A.length;
		final int n = problem.A[0].length;
		final int[] bounds = new int[m];
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				bounds[i] += problem.A[i][j];
			}
		}
		final IntVec boundsVec = new IntVec(bounds);
		final Sequencer seq = new SeqLE(boundsVec,boundsVec.dim(),boundsVec.dim()-1);
		final DivideAndConquerCounter dc = new DivideAndConquerCounter(problem,false,true,false);
		final Map<IntVec,BigInteger> solnCounts = new HashMap<IntVec,BigInteger>(); // synchronize access to this
		final IntFunc f = new IntFunc() {
			@Override
			public BigInteger f(final int[] x) {
				final int lastValue = x[0];
				final int m = boundsVec.dim();
				final int[] b = new int[m];
				b[m-1] = lastValue;
				do {
					if(ZeroOneStore.wantB(problem,b)) {
						final BigInteger nsolns = dc.countNonNegativeSolutions(b);
						if(nsolns.compareTo(BigInteger.ZERO)>0) {
							final IntVec key = new IntVec(b);
							synchronized (solnCounts) {
								solnCounts.put(key,nsolns);
							}
						}
					}
				} while(seq.advance(b));
				return BigInteger.ZERO;
			}
		};
		final Sequencer seqL = new RangeIter(0,bounds[m-1]+1);
		final boolean runParallel = true;
		final Reducer summer = runParallel?new ThreadedSum():new SimpleSum();
		summer.reduce(f,seqL);
		return solnCounts;
	}
	
	
	public static void main(final String[] args) {
		System.out.println();
		for(int n=1;n<=6;++n) {
			System.out.println();
			System.out.println("" + n + " by " + n + " contingency tables");
			final CountingProblem prob  = new ContingencyTableProblem(n,n);
			System.out.println(new Date());
			final DivideAndConquerCounter dc = new DivideAndConquerCounter(prob,true, false,true);
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


	@Override
	public int cacheSize() {
		return underlying.cacheSize();
	}


	@Override
	public void clearCache() {
		underlying.clearCache();
	}

}
