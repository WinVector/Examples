package com.mzlabs.count.zeroone;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.NonNegativeIntegralCounter;
import com.mzlabs.count.divideandconquer.DivideAndConquerCounter;
import com.mzlabs.count.util.IntLinOp;
import com.mzlabs.count.util.IntVec;
import com.mzlabs.count.util.Permutation;
import com.winvector.linalg.DenseVec;
import com.winvector.linalg.LinalgFactory;
import com.winvector.linalg.Matrix;
import com.winvector.linalg.jblas.JBlasMatrix;
import com.winvector.lp.LPEQProb;
import com.winvector.lp.LPException;
import com.winvector.lp.LPSoln;
import com.winvector.lp.impl.RevisedSimplexSolver;

/**
 * Count number of non-negative integer solutions to a linear system of equalities using
 * the even/odd method from:
 * @article{CPC:54639,
 * author = {MOUNT,JOHN},
 * title = {Fast Unimodular Counting},
 * journal = {Combinatorics, Probability and Computing},
 * volume = {9},
 * issue = {03},
 * month = {5},
 * year = {2000},
 * issn = {1469--2163},
 * pages = {277--285},
 * numpages = {9},
 * doi = {null}
 * }
 * 
 * Linear system must be such that x=0 is unique non-negative solution to A x = 0.
 * 
 * @author johnmount
 *
 */
public final class ZeroOneCounter implements NonNegativeIntegralCounter {
	private final CountingProblem prob;
	private final int m;
	private final ZeroOneStore zeroOneCounts;
	
	/**
	 * check that x = 0 is the unique non-negative solution to A x = 0
	 * @param A
	 * @throws LPException 
	 */
	private static <Z extends Matrix<Z>> String matrixFlaw(final LinalgFactory<Z> factory, final int[][] A) {
		final int m = A.length;
		final int n = A[0].length;
		// check for empty columns (LP does catch these, but easier to read message if we get them here)
		for(int j=0;j<n;++j) {
			boolean sawNZValue = false;
			for(int i=0;i<m;++i) {
				if(A[i][j]!=0) {
					sawNZValue = true;
					break;
				}
			}
			if(!sawNZValue) {
				return "matrix column " + j + " is all zero (unbounded or empty system)";
			}
		}
		try {
			final Z am = factory.newMatrix(m,n,false);
			for(int i=0;i<m;++i) {
				for(int j=0;j<n;++j) {
					if(A[i][j]!=0) {
						am.set(i, j, A[i][j]);
					}
				}
			}
			final double[] c = new double[n];
			Arrays.fill(c,-1.0);
			final LPEQProb prob = new LPEQProb(am.columnMatrix(),new double[m],new DenseVec(c));
			final RevisedSimplexSolver solver = new RevisedSimplexSolver();
			final LPSoln soln = solver.solve(prob, null, 0.0, 1000, factory);
			final double[] x = soln.primalSolution.toArray(n);
			boolean bad = false;
			for(final double xi: x) {
				if(Math.abs(xi)>1.0e-6) {
					bad = true;
					break;
				}
			}
			if(bad) {
				return "strictly positive solution to A x = 0: ";
			}
			return null; // no problem
		} catch (LPException ex) {
			return ex.toString();
		}
	}
	
	
	/**
	 * build all the zero/one lookup tables using a simple enumerate all zero one interiors (2^n complexity, not the n^m we want)
	 * @param A
	 * @return map from modul-2 class of rhs to rhs to count
	 */
	public static Map<IntVec,BigInteger> zeroOneSolutionCounts(final int[][] A) {
		final Map<IntVec,BigInteger> zeroOneCounts = new HashMap<IntVec,BigInteger>(10000);
		final int m = A.length;
		final int n = A[0].length;
		// build all possible zero/one sub-problems
		final IntLinOp Aop = new IntLinOp(A);
		final int[] z = new int[n];
		final int[] r = new int[m];
		do {
			Aop.mult(z,r);
			final IntVec rvec = new IntVec(r);
			BigInteger nzone = zeroOneCounts.get(rvec);
			if(null==nzone) {
				nzone = BigInteger.ONE;
			} else {
				nzone = nzone.add(BigInteger.ONE);
			}
			zeroOneCounts.put(rvec,nzone);
		} while(IntVec.advanceLT(2,z));
		return zeroOneCounts;
	}
	

	
	/**
	 * 
	 * @param A a matrix where x=0 is the unique non-negative solution to A x = 0
	 */
	public ZeroOneCounter(final CountingProblem prob, final boolean useSDQZO) {
		this.prob = prob;
		m = prob.A.length;
		// check conditions
		final String problem = matrixFlaw(JBlasMatrix.factory,prob.A);
		if(null!=problem) {
			throw new IllegalArgumentException("unnacceptable matrix: " + problem);
		}
		// build all possible zero/one sub-problems
		final Map<IntVec,BigInteger> countsByB;
		if(useSDQZO) {
			countsByB = DivideAndConquerCounter.zeroOneSolutionCounts(prob);
		} else {
			countsByB = zeroOneSolutionCounts(prob.A);
		}
		zeroOneCounts = new ZeroOneStore(prob,countsByB);
	}
	

	

	
	/**
	 * assumes finite number of solutions (all variables involved) and A non-negative
	 * @param b non-negative vector already in normal problem normal form
	 * @return number of non-negative integer solutions x to A x == b
	 */
	private BigInteger countNonNegativeSolutionsR(final IntVec b, final Map<IntVec,BigInteger> nonnegCounts) {
		// check for base cases
		if(!prob.admissableB(b.asVec())) {
			return BigInteger.ZERO;
		}
		if(b.isZero()) {
			return BigInteger.ONE;
		}
		BigInteger cached = nonnegCounts.get(b);
		if(null==cached) {
			cached = BigInteger.ZERO;
			final Map<IntVec,BigInteger> group = zeroOneCounts.lookup(b);
			if((null!=group)&&(!group.isEmpty())) {
				final int[] bprime = new int[m];
				for(final Map.Entry<IntVec,BigInteger> me: group.entrySet()) {
					final IntVec r = me.getKey();
					boolean goodR = true;
					for(int i=0;i<m;++i) {
						final int diff = b.get(i) - r.get(i);
						if((diff<0)||((diff&0x1)!=0)) {
							goodR = false;
							break;
						}
					}
					if(goodR) {
						final BigInteger nzone = me.getValue();
						for(int i=0;i<m;++i) {
							bprime[i] = (b.get(i) - r.get(i))/2;
						}
						final Permutation tobprimeNorm = prob.toNormalForm(bprime);
						final IntVec bprimeNorm = new IntVec(tobprimeNorm.apply(bprime));
						final BigInteger subsoln = countNonNegativeSolutionsR(bprimeNorm,nonnegCounts);
						cached = cached.add(nzone.multiply(subsoln));
					}
				}
			}
			nonnegCounts.put(b,cached);
			//System.out.println(b + " " + cached);
		}
		return cached;
	}
	
	public BigInteger countNonNegativeSolutions(final int[] bIn) {
		for(final int bi: bIn) {
			if(bi<0) {
				throw new IllegalArgumentException("negative b entry");
			}
		}
		if(!prob.admissableB(bIn)) {
			return BigInteger.ZERO;
		}
		final Permutation perm = prob.toNormalForm(bIn);
		final IntVec bNormal = new IntVec(perm.apply(bIn));
		final HashMap<IntVec, BigInteger> cache = new HashMap<IntVec,BigInteger>(10000);
		final BigInteger result = countNonNegativeSolutionsR(bNormal,cache);
		//final Set<BigInteger> values = new HashSet<BigInteger>(cache.values());
		//System.out.println("cached " + cache.size() + " keys for " + values.size() + " values");
		return result;
	}
	




	/**
	 * assumes all variables involved and A non-negative and no empty columns
	 * @param A
	 * @param b
	 * @return number of non-negative (or zero/one) integer solutions of A x = b
	 */
	public static BigInteger bruteForceSolnDebug(final int[][] A, final int[] b, final boolean zeroOne) {
		final int m = A.length;
		final int n = A[0].length;
		// inspect that A meets assumed conditions
		final boolean[] sawPos = new boolean[n];
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				if(A[i][j]<0) {
					throw new IllegalArgumentException("negative matrix entry");
				}
				if(A[i][j]>0) {
					sawPos[j] = true;
				}
			}
		}
		for(final boolean pi: sawPos) {
			if(!pi) {
				throw new IllegalArgumentException("empty matrix column");
			}
		}
		final int[] bounds = new int[n];
		Arrays.fill(bounds,Integer.MAX_VALUE);
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				if(A[i][j]>0) {
					bounds[j] = Math.min(bounds[j],b[i]/A[i][j]);
				}
			}
		}
		if(zeroOne) {
			for(int j=0;j<n;++j) {
				bounds[j] = Math.min(1,bounds[j]);
			}
		}
		final IntVec boundsV = new IntVec(bounds);
		BigInteger count = BigInteger.ZERO;
		final int[] x = new int[n];
		final int[] r = new int[m];
		do {
			IntLinOp.mult(A,x,r);
			boolean goodR = true;
			for(int i=0;i<m;++i) {
				if(b[i]!=r[i]) {
					goodR = false;
					break;
				}
			}
			if(goodR) {
				count = count.add(BigInteger.ONE);
			}
		} while(boundsV.advanceLE(x));
		return count;
	}
	
	

}
