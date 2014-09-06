package com.mzlabs.count.divideandconquer;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.SortedSet;
import java.util.TreeSet;

import com.mzlabs.count.IntVec;

public final class IntMat implements Comparable<IntMat> {
	private final int hashCode;
	private final int[][] A;
	
	public IntMat(final int[][] A) {
		final int m = A.length;
		final int n = A[0].length;
		this.A = new int[m][];
		int hc = 0;
		for(int i=0;i<m;++i) {
			this.A[i] = Arrays.copyOf(A[i],n);
			hc += Arrays.hashCode(A[i]);
		}
		hashCode = hc;
	}

	@Override
	public int compareTo(final IntMat o) {
		if(hashCode!=o.hashCode) {
			if(hashCode>=o.hashCode) { 
				return 1;
			} else {
				return -1;
			}
		}
		final int m = A.length;
		if(m!=o.A.length) {
			if(m>=o.A.length) {
				return 1;
			} else {
				return -1;
			}
		}
		final int n = A[0].length;
		if(n!=o.A[0].length) {
			if(n>=o.A[0].length) {
				return 1;
			} else {
				return -1;
			}
		}
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				if(A[i][j]!=o.A[i][j]) {
					if(A[i][j]>=o.A[i][j]) {
						return 1;
					} else {
						return -1;
					}
				}
			}
		}
		return 0;
	}
	
	@Override
	public boolean equals(final Object o) {
		return compareTo((IntMat)o)==0;
	}
	
	@Override
	public int hashCode() {
		return hashCode;
	}

	public static final class RowDescription {
		public final int origIndex;  
		public final boolean isZeroRow;
		public final int newIndex; // -1 for all non-primary rows
		public final int matchingOldIndex; // where primary row is mapped from, -1 for zero and primary rows
		public RowDescription(final int origIndex, final boolean isZeroRow, final int newIndex, final int matchingOldIndex) {
			this.origIndex = origIndex;
			this.isZeroRow = isZeroRow;
			this.newIndex = newIndex;
			this.matchingOldIndex = matchingOldIndex;
		}
		
		@Override
		public String toString() {
			return "(" + origIndex + ":" + isZeroRow + ";" + newIndex + "," + matchingOldIndex + ")";
		}
	}
	
	public static RowDescription[] buildMapToCannon(final int[][] A, boolean sort) {
		final int m = A.length;
		final Map<IntVec,Integer> indexMap = new HashMap<IntVec,Integer>();
		if(sort) {
			final SortedSet<IntVec> orderedSet = new TreeSet<IntVec>();
			for(int i=0;i<m;++i) {
				final IntVec key = new IntVec(A[i]);
				if((!key.isZero())&&(!orderedSet.contains(key))) {
					orderedSet.add(key);
				}
			}
			for(final IntVec v: orderedSet) {
				indexMap.put(v,indexMap.size());
			}
		} else {
			for(int i=0;i<m;++i) {
				final IntVec key = new IntVec(A[i]);
				if((!key.isZero())&&(!indexMap.containsKey(key))) {
					indexMap.put(key,indexMap.size());
				}
			}
		}
		final Map<IntVec,RowDescription> rowMap = new HashMap<IntVec,RowDescription>();
		final RowDescription[] descr = new RowDescription[m];
		for(int i=0;i<m;++i) {
			final IntVec key = new IntVec(A[i]);
			if(key.isZero()) {
				descr[i] = new RowDescription(i,true,-1,-1);
			} else {
				RowDescription peerDescr = rowMap.get(key);
				if(null==peerDescr) {
					descr[i] = new RowDescription(i,false,indexMap.get(key),-1);
					rowMap.put(key,descr[i]);
				} else {
					descr[i] = new RowDescription(i,false,-1,peerDescr.origIndex);
				}
			}
		}
		return descr;
	}
	
	public static int[] mapVector(final RowDescription[] rowDescr, final int[] b) {
		int m2 = 0;
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				++m2;
			}
		}
		final int[] b2 = new int[m2];
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				b2[di.newIndex] = b[di.origIndex];
			}
		}
		return b2;
	}
	
	/**
	 * // TODO: add test
	 * @param A m by n matrix (m,n>0)
	 * @return
	 */
	public static int[] nonZeroRows(final int[][] A) {
		final int m = A.length;
		final int n = A[0].length;
		if((m<=0)||(n<=0)) {
			throw new IllegalArgumentException("degenerate matrix");
		}
		final boolean[] sawNZ = new boolean[m];
		for(int i=0;i<m;++i) {
			for(int j=0;j<n;++j) {
				if(A[i][j]!=0) {
					sawNZ[i] = true;
				}
			}
		}
		int nnz = 0;
		for(int i=0;i<m;++i) {
			if(sawNZ[i]) {
				++nnz;
			}
		}
		final int[] nzRows = new int[nnz];
		nnz = 0;
		for(int i=0;i<m;++i) {
			if(sawNZ[i]) {
				nzRows[nnz] = i;
				++nnz;
			}
		}
		return nzRows;
	}
	
	// TODO: add test
	public static int[][] rowRestrict(final int[][] A, final RowDescription[] rowDescr) {
		int m2 = 0;
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				++m2;
			}
		}
		final int n = A[0].length;
		final int[][] A2 = new int[m2][];
		for(final RowDescription di: rowDescr) {
			if(di.newIndex>=0) {
				A2[di.newIndex] = Arrays.copyOf(A[di.origIndex],n);
			}
		}
		return A2;
	}
	
	// TODO: add test
	public static int[][] colRestrict(final int[][] A, final int[] cols) {
		final int m = A.length;
		final int n2 = cols.length;
		final int[][] A2 = new int[m][n2];
		for(int i=0;i<m;++i) {
			for(int j2=0;j2<n2;++j2) {
				final int j = cols[j2];
				A2[i][j2] = A[i][j];
			}
		}
		return A2;
	}
}
