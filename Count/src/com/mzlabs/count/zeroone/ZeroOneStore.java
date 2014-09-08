package com.mzlabs.count.zeroone;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;

import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.util.IntVec;
import com.mzlabs.count.util.Permutation;

public final class ZeroOneStore {
	private final CountingProblem problem;
	private final Map<IntVec,Map<IntVec,BigInteger>> modulusToRhsToZOCountThin;
	
	private static IntVec mod2Vec(final IntVec x) {
		final int n = x.dim();
		final int[] xm = new int[n];
		for(int i=0;i<n;++i) {
			xm[i] = x.get(i)%2;			
		}
		return new IntVec(xm);
	}
	
	public static boolean wantB(final CountingProblem problem, final int[] b) {
		if(!problem.admissableB(b)) {
			return false;
		}
		final int n = b.length;
		final int[] xm = new int[n];
		for(int i=0;i<n;++i) {
			xm[i] = b[i]%2;			
		}
		final Permutation perm = problem.toNormalForm(xm);
		final int[] sorted = perm.apply(xm);
		for(int i=0;i<n;++i) {
			if(sorted[i]!=xm[i]) {
				return false;
			}
		}
		return true;
	}
	
	/**
	 * 
	 * @param counts Map b to number of solutions to A z = b for z zero/one (okay to omit unsolvable systems) we only need the
	 * 		  b such that mod2Vec(b) is already in normal form.
	 * @return Map from (b mod 2) to b to number of solutions to A z = b (all unsolvable combination omitted)
	 */
	private static Map<IntVec,Map<IntVec,BigInteger>> organizeZeroOneStructures(final CountingProblem problem,
			final Map<IntVec,BigInteger> counts) {
		final Map<IntVec,Map<IntVec,BigInteger>> modulusToRhsToZOCount = new HashMap<IntVec,Map<IntVec,BigInteger>>(1000);
		for(final Map.Entry<IntVec,BigInteger> me: counts.entrySet()) {
			final IntVec b = me.getKey();
			final BigInteger c = me.getValue();
			if((c.compareTo(BigInteger.ZERO)>0)&&wantB(problem,b.asVec())) {
				final IntVec groupVec = mod2Vec(b);
				Map<IntVec,BigInteger> bgroup = modulusToRhsToZOCount.get(groupVec);
				if(null==bgroup) {
					bgroup = new HashMap<IntVec,BigInteger>();
					modulusToRhsToZOCount.put(groupVec,bgroup);
				}
				final BigInteger ov = bgroup.get(b);
				if(null==ov) {
					bgroup.put(b,c);
				} else {
					if(ov.compareTo(c)!=0) {
						throw new IllegalArgumentException("zero one data doesn't obey expected symmetries");
					}
				}
			}
		}
		return modulusToRhsToZOCount;
	}
	
	public ZeroOneStore(final CountingProblem problem, final Map<IntVec,BigInteger> counts) {
		this.problem = problem;
		modulusToRhsToZOCountThin = organizeZeroOneStructures(problem,counts);
	}

	public Map<IntVec, BigInteger> lookup(final IntVec b) {
		final IntVec groupVec = mod2Vec(b);
		final int[] groupVecA = groupVec.asVec();
		final Permutation perm = problem.toNormalForm(groupVecA);
		final IntVec sortedGroupVec = new IntVec(perm.apply(groupVecA));
		final Map<IntVec, BigInteger> mpRow = modulusToRhsToZOCountThin.get(sortedGroupVec);
		final Map<IntVec,BigInteger> mpAnswer;
		if(null!=mpRow) {
			mpAnswer = new HashMap<IntVec,BigInteger>(3*mpRow.size() + 100);
			for(final Map.Entry<IntVec,BigInteger> me: mpRow.entrySet()) {
				final IntVec origKey = me.getKey();
				final BigInteger count = me.getValue();
				final IntVec newKey = new IntVec(perm.applyInv(origKey.asVec()));
				mpAnswer.put(newKey,count);
			}
		} else {
			mpAnswer = null;
		}
		return mpAnswer;
	}
}
