package com.mzlabs.count.util;

import java.util.Arrays;
import java.util.SortedSet;
import java.util.TreeSet;

public final class Permutation implements Comparable<Permutation> {
	private final int[] perm;
	
	public Permutation(final int[] perm) {
		this.perm = perm;
	}
	
	public Permutation(final int n) {
		this.perm = new int[n];
		for(int i=0;i<n;++i) {
			perm[i] = i;
		}
	}
	
	private static final class SortItem implements Comparable<SortItem> {
		public final int origIndex;
		public final int value;

		public SortItem(final int origIndex, final int value) {
			this.origIndex = origIndex;
			this.value = value;
		}
		
		@Override
		public int compareTo(final SortItem o) {
			if(value!=o.value) {
				if(value>=o.value) {
					return 1;
				} else {
					return -1;
				}
			}
			if(origIndex!=o.origIndex) {
				if(origIndex>=o.origIndex) {
					return 1;
				} else {
					return -1;
				}
			}
			return 0;
		}
		
		@Override
		public boolean equals(final Object o) {
			return compareTo((SortItem)o)==0;
		}

		@Override
		public int hashCode() {
			return origIndex;
		}
		
		@Override
		public String toString() {
			return "" + origIndex + ":" + value;
		}
	}
	
	public final int dim() {
		return perm.length;
	}
	
	@Override
	public int compareTo(final Permutation o) {
		if(perm.length!=o.perm.length) {
			if(perm.length>=o.perm.length) {
				return 1;
			} else {
				return -1;
			}
		}
		return IntVec.compare(perm,o.perm);
	}
	
	@Override
	public boolean equals(final Object o) {
		return compareTo((Permutation)o)==0;
	}
	
	@Override
	public int hashCode() {
		return Arrays.hashCode(perm);
	}
	
	@Override
	public String toString() {
		final StringBuilder b = new StringBuilder();
		final SortedSet<Integer> pending = new TreeSet<Integer>(); 
		final int n = perm.length;
		for(int i=0;i<n;++i) {
			pending.add(i);
		}
		while(!pending.isEmpty()) {
			final Integer k = pending.first();
			pending.remove(k);
			if(perm[k]!=k) {
				b.append("(");
				b.append(k);
				int pt = perm[k];
				while(pending.contains(pt)) {
					b.append(" " + pt);
					pending.remove(pt);
					pt = perm[pt];
				}
				b.append(")");
			}
		}
		return b.toString();
	}
	
	/**
	 * 
	 * @param x
	 * @return perm(x)
	 */
	public int[] apply(final int[] x) {
		final int n = perm.length;
		final int[] r = new int[n];
		for(int i=0;i<n;++i) {
			r[perm[i]] = x[i];
		}
		return r;
	}
	
	/**
	 * 
	 * @param x
	 * @return (inv(perm))(x)
	 */
	public int[] applyInv(final int[] x) {
		final int n = perm.length;
		final int[] r = new int[n];
		for(int i=0;i<n;++i) {
			r[i] = x[perm[i]];
		}
		return r;		
	}
	
	/**
	 * @param p permutation on with p.length=o.p.length
	 * @return new perm r s.t. r(x) = p(this(x)), compatible with Herstein circle notation (T o P)(x) = P(T(x)) (p. 13, Topics in Algebra 2nd edition)
	 */
	public Permutation compose(final Permutation p) {
		final int[] r = Arrays.copyOf(p.perm,perm.length);
		return new Permutation(apply(r));
	}
	
	/**
	 * 
	 * @param d
	 * @param fromIndex
	 * @param toBound
	 * @param totalLength
	 * @return a permutation of length totalLength that sorts the in d from fromIndex until (not including) toBound
	 */
	public static Permutation sortingPerm(final int[] d, final int fromIndex, final int toBound, final int totalLength) {
		final int[] p = new int[totalLength];
		for(int i=0;i<totalLength;++i) {
			p[i] = i;
		}
		final int n = toBound-fromIndex;
		final SortItem[] items = new SortItem[n];
		for(int i=0;i<n;++i) {
			items[i] = new SortItem(i+fromIndex,d[i+fromIndex]);
		}
		Arrays.sort(items);
		for(int i=0;i<n;++i) {
			final int origIndex = items[i].origIndex;
			final int newIndex = i + fromIndex;
			p[origIndex] = newIndex;
		}
		return new Permutation(p);
	}
}
