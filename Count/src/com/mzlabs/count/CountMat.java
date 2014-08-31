package com.mzlabs.count;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;

/**
 * Count number of non-negative integer solutions to a linear system of equalities using
 * the even/odd method from 
 * @article{CPC:54639,
 * author = {MOUNT,JOHN},
 * title = {Fast Unimodular Counting},
 * journal = {Combinatorics, Probability and Computing},
 * volume = {9},
 * issue = {03},
 * month = {5},
 * year = {2000},
 * issn = {1469-2163},
 * pages = {277--285},
 * numpages = {9},
 * doi = {null},
 * URL = {http://journals.cambridge.org/article_S0963548300004193},
 * }
 * @author johnmount
 *
 */
public final class CountMat {
	
	private final int m;
	private final int n;
	private final Map<IntVec,Map<IntVec,BigInteger>> zeroOneCounts = new HashMap<IntVec,Map<IntVec,BigInteger>>(10000);
	
	/**
	 * 
	 * @param A a non-negative matrix with no zero columns
	 */
	public CountMat(final int[][] A) {
		m = A.length;
		n = A[0].length;
		// check conditions
		final boolean[] sawNZ = new boolean[n];
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				if(A[i][j]<0) {
					throw new IllegalArgumentException("negative matrix entry");
				}
				if(A[i][j]>0) {
					sawNZ[j] = true;
				}
			}
		}
		for(int j=0;j<n;++j) {
			if(!sawNZ[j]) {
				throw new IllegalArgumentException("zero column in matrix");
			}
		}
		// build all possible zero/one sub-problems
		final IntLinOp Aop = new IntLinOp(A);
		final int[] z = new int[n];
		final int[] r = new int[m];
		do {
			Aop.mult(z,r);
			final IntVec rvec = new IntVec(r);
			final IntVec groupVec = modKVec(2,rvec);
			Map<IntVec,BigInteger> rgroup = zeroOneCounts.get(groupVec);
			if(null==rgroup) {
				rgroup = new HashMap<IntVec,BigInteger>();
				zeroOneCounts.put(groupVec,rgroup);
			}
			BigInteger nzone = rgroup.get(rvec);
			if(null==nzone) {
				nzone = BigInteger.ONE;
			} else {
				nzone = nzone.add(BigInteger.ONE);
			}
			rgroup.put(rvec,nzone);
		} while(advance(2,z));
	}
	
	private static IntVec modKVec(final int k, final IntVec x) {
		final int n = x.dim();
		final int[] xm = new int[n];
		for(int i=0;i<n;++i) {
			xm[i] = x.get(i)%k;			
		}
		return new IntVec(xm);
	}
	
	/**
	 * advance a non-negative through all non-negative combinations less than bound, (starting at all zeros)
	 * @param bvec
	 * @return true if we haven't wrapped around to all zeros
	 */
	public static boolean advance(final int bound, final int[] bvec) {
		final int n = bvec.length;
		final int boundMinus1 = bound-1;
		// look for right-most advancable item
		for(int i=n-1;i>=0;--i) {
			if(bvec[i]<boundMinus1) {
				bvec[i] += 1;
				return true;
			}
			bvec[i] = 0;
		}
		return false;
	}
	
	/**
	 * assumes finite number of solutions (all variables involved) and A non-negative
	 * @param b non-negative vector
	 * @return number of non-negative integer solutions x to A x == b
	 */
	private BigInteger countNonNegativeSolutions(final IntVec b, final Map<IntVec,BigInteger> nonnegCounts) {
		// check for base case
		if(b.isZero()) {
			return BigInteger.ONE;
		}
		BigInteger cached = nonnegCounts.get(b);
		if(null==cached) {
			cached = BigInteger.ZERO;
			final IntVec groupVec = modKVec(2,b);
			final Map<IntVec,BigInteger> group = zeroOneCounts.get(groupVec);
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
						final BigInteger subsoln = countNonNegativeSolutions(new IntVec(bprime),nonnegCounts);
						cached = cached.add(nzone.multiply(subsoln));
					}
				}
				nonnegCounts.put(b,cached);
				//System.out.println(b + " " + cached);
			}
		}
		return cached;
	}
	
	public BigInteger countNonNegativeSolutions(final int[] b) {
		for(final int bi: b) {
			if(bi<0) {
				throw new IllegalArgumentException("negative b entry");
			}
		}
		return countNonNegativeSolutions(new IntVec(b),new HashMap<IntVec,BigInteger>(10000));
	}

	/**
	 * assumes all variables involved and A non-negative
	 * @param A
	 * @param b
	 * @return number of non-negative integer solutions of A x = b
	 */
	public static BigInteger bruteForceSolnDebug(final int[][] A, final int[] b) {
		int bound = 0;
		for(final int bi: b) {
			bound = Math.max(bound,bi+1);
		}
		BigInteger count = BigInteger.ZERO;
		final int m = A.length;
		final int n = A[0].length;
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
		} while(advance(bound,x));
		return count;
	}
	
	

}
