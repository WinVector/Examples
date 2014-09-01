package com.mzlabs.count;

import static org.junit.Assert.assertEquals;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;

/**
 * build every possible b such that A z = b is solvable for z in zero/one for zero/one matrix A with no zero columns
 * useful when there are many more columns than rows
 * 
 * Not practical- slower than the naive method of enumerating all zero/one z's for contingency tables until we get to probably around 20 by 20 tables.
 * 
 * @author johnmount
 *
 */

final class DivideAndConquer {
	private final int[][] A;
	private final Map<DKey,BigInteger> cache = new HashMap<DKey,BigInteger>(1000);
	
	
	public static boolean acceptableA(final int[][] A) {
		final int m = A.length;
		final int n = A[0].length;
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
	
	/**
	 * 
	 * @param A non-negative zero/one matrix with no zero columns
	 */
	private DivideAndConquer(final int[][] A) {
		this.A = A;
		if(!acceptableA(A)) {
			throw new IllegalArgumentException("unaccaptable matrix");
		}
	}
	
	/**
	 * advance a non-negative through all non-negative combinations less than equal to bound, (starting at all zeros)
	 * @param bvec
	 * @return true if we haven't wrapped around to all zeros
	 */
	private static boolean advanceEq(final IntVec bound, final int[] bvec) {
		final int n = bvec.length;
		// look for right-most advancable item
		for(int i=n-1;i>=0;--i) {
			if(bvec[i]<bound.get(i)) {
				bvec[i] += 1;
				return true;
			}
			bvec[i] = 0;
		}
		return false;
	}

	/**
	 * return number of solutions to A[colset] z = b with z zero/one
	 * @param b
	 * @return
	 */
	private BigInteger solutionCount(final DKey key) {
		// check for base cases
		final int m = A.length;
		if(key.b.isZero()) {
			return BigInteger.ONE;
		}
		if(key.columnSet.dim()<=0) {
			if(key.b.isZero()) {
				return BigInteger.ONE;
			} else {
				return BigInteger.ZERO;
			}
		}
		if(key.columnSet.dim()==1) {
			final int j = key.columnSet.get(0);
			boolean sawSoln = false;
			int soln = 0;
			for(int i=0;i<m;++i) {
				if(A[i][j]!=0) {
					final int x = key.b.get(i)/A[i][j];
					if((x<0)||(x>1)||(x*A[i][j]!=key.b.get(i))) {
						return BigInteger.ZERO;
					}
					if(!sawSoln) {
						sawSoln = true;
						soln = x;
					} else {
						if(x!=soln) {
							return BigInteger.ZERO;
						}
					}
				} else {
					if(key.b.get(i)!=0) {
						return BigInteger.ZERO;
					}
				}
			}
			return BigInteger.ONE;
		}
		BigInteger cached = cache.get(key);
		if(null==cached) {
			//System.out.println(key);
			// know we have at least 2 columns
			cached = BigInteger.ZERO;
			final int n1 = key.columnSet.dim()/2;
			final int n2 = key.columnSet.dim() - n1;
			final IntVec c1;
			{
				final int[] cset1 = new int[n1];
				for(int j=0;j<n1;++j) {
					cset1[j] = key.columnSet.get(j);
				}
				c1 = new IntVec(cset1);
			}
			final IntVec c2;
			{
				final int[] cset2 = new int[n2];
				for(int j=0;j<n2;++j) {
					cset2[j] = key.columnSet.get(j+n1);
				}
				c2 = new IntVec(cset2);				
			}
			final int[] b1 = new int[m];
			final int[] b2 = new int[m];
			do {
				final DKey k1 = new DKey(c1,new IntVec(b1));
				final BigInteger sub1 = solutionCount(k1);
				if(sub1.compareTo(BigInteger.ZERO)>0) {
					for(int i=0;i<m;++i) {
						b2[i] = key.b.get(i) - b1[i];
					}
					final DKey k2 = new DKey(c2,new IntVec(b2));
					final BigInteger sub2 = solutionCount(k2);
					if(sub2.compareTo(BigInteger.ZERO)>0) {
						cached = cached.add(sub1.multiply(sub2));
					}
				}
			} while(advanceEq(key.b,b1));
			cache.put(key,cached);
		}
		return cached;
	}
	
	/**
	 * return number of solutions to A z = b with z zero/one
	 * @param b
	 * @return
	 */
	private BigInteger solutionCount(final int[] b) {
		final int n = A[0].length;
		final IntVec bvec = new IntVec(b);
		final int[] colset = new int[n];
		for(int i=0;i<n;++i) {
			colset[i] = i;
		}
		final DKey key = new DKey(new IntVec(colset),bvec);
		return solutionCount(key);
	}
	
	/**
	 * 
	 * @return map from every b such that A z = b is solvable for z zero/one to how many such z there are
	 */
	public static Map<IntVec,BigInteger> solutionCounts(final int[][] A) {
		final DivideAndConquer dc = new DivideAndConquer(A);
		final Map<IntVec,BigInteger> solnCounts = new HashMap<IntVec,BigInteger>();
		final int m = A.length;
		final int n = A[0].length;
		final int[] bounds = new int[m];
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				bounds[i] += A[i][j];
			}
		}
		final IntVec boundsVec = new IntVec(bounds);
		final int[] b = new int[m];
		do {
			final BigInteger nsolns = dc.solutionCount(b);
			if(nsolns.compareTo(BigInteger.ZERO)>0) {
				solnCounts.put(new IntVec(b),nsolns);
			}
		} while(advanceEq(boundsVec,b));
		System.out.println("dc cache size: " + dc.cache.size());
		System.out.println("dc result size: " + solnCounts.size());
		BigInteger total = BigInteger.ZERO;
		for(final BigInteger ci: solnCounts.values()) {
			total = total.add(ci);
		}
		System.out.println("dc total solns: " + total);
		System.out.println("dc m,n,2^n: " + m + " " + n + " " + Math.pow(2,n));
		return solnCounts;
	}
	
	public static void main(final String[] args) {
		final int[][] A = CountExample.contingencyTable(3,3);
		final Map<IntVec,BigInteger> z1 = CountMat.buildZeroOneStructures(A);
		final Map<IntVec,BigInteger> z2 = DivideAndConquer.solutionCounts(A);
		assertEquals(z1.size(),z2.size());
		for(final Map.Entry<IntVec,BigInteger> me: z1.entrySet()) {
			final IntVec b = me.getKey();
			final BigInteger c1 = me.getValue();
			final BigInteger c2 = z2.get(b);
			assertEquals(0,c1.compareTo(c2));
		}
	}
}
