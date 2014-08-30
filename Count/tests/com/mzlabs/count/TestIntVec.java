package com.mzlabs.count;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;

import java.util.HashSet;
import java.util.Set;

import org.junit.Test;

public class TestIntVec {
	@Test
	public void testZero() {
		final IntVec iv0 = new IntVec(new int[] {0,0,0});
		assertTrue(iv0.isZero());
	}
	
	@Test
	public void testNonZero() {
		final IntVec ivnz = new IntVec(new int[] {0,1,0});
		assertFalse(ivnz.isZero());
	}
	
	@Test
	public void testContents() {
		final int[] a = new int[] {1, 2, 3};
		final IntVec v = new IntVec(a);
		assertEquals(a.length,v.dim());
		for(int i=0;i<a.length;++i) {
			assertEquals(a[i],v.get(i));
		}
	}
	
	@Test
	public void testComp() {
		final IntVec iv0 = new IntVec(new int[] {0,0,0});
		final IntVec ivnz = new IntVec(new int[] {0,1,0});
		final Set<IntVec> s = new HashSet<IntVec>();
		for(final IntVec v : new IntVec[] {iv0, ivnz}) {
			assertTrue(v.compareTo(v)==0);
			assertTrue(v.equals(v));
			s.add(v);
		}
		assertEquals(2,s.size());
		assertTrue(iv0.compareTo(ivnz)!=0);
		assertFalse(iv0.equals(ivnz));
		assertFalse(iv0.toString().compareTo(ivnz.toString())==0);
	}
}
