package com.mzlabs.count;



/**
 * represent the choice of a right-hand side of A x = b and a set of columns from A
 * @author johnmount
 *
 */
final class DKey implements Comparable<DKey> {
	private final int hashCode;
	public final IntVec columnSet;
	public final IntVec b;
	
	public DKey(final IntVec columnSet, final IntVec b) {
		this.columnSet = columnSet;
		this.b = b;
		this.hashCode = b.hashCode() + 7*columnSet.hashCode();
	}

	@Override
	public int compareTo(final DKey o) {
		if(hashCode!=o.hashCode) {
			if(hashCode>=o.hashCode) {
				return 1;
			} else {
				return -1;
			}
		}
		final int cmp1 = b.compareTo(o.b);
		if(0!=cmp1) {
			return cmp1;
		}
		return columnSet.compareTo(o.columnSet);
	}
	
	@Override
	public boolean equals(final Object o) {
		return compareTo((DKey)o)==0;
	}
	
	@Override
	public int hashCode() {
		return hashCode;
	}
	
	@Override
	public String toString() {
		return columnSet.toString() + ":" + b;
	}
}