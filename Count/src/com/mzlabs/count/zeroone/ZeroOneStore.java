package com.mzlabs.count.zeroone;

import java.math.BigInteger;
import java.util.HashMap;
import java.util.Map;

import com.mzlabs.count.CountingProblem;
import com.mzlabs.count.util.IntVec;
import com.mzlabs.count.util.Permutation;

final class ZeroOneStore {
	private final CountingProblem problem;
	private final Map<IntVec,Map<IntVec,BigInteger>> modulusToRhsToZOCount;
	private final Map<IntVec,Map<IntVec,BigInteger>> modulusToRhsToZOCountThin;
	
	private static IntVec mod2Vec(final IntVec x) {
		final int n = x.dim();
		final int[] xm = new int[n];
		for(int i=0;i<n;++i) {
			xm[i] = x.get(i)%2;			
		}
		return new IntVec(xm);
	}
	
	/**
	 * 
	 * @param counts Map b to number of solutions to A z = b for z zero/one (okay to omit unsolvable systems)
	 * @return Map from (b mod 2) to b to number of solutions to A z = b (all unsolvable combination omitted)
	 */
	private static Map<IntVec,Map<IntVec,BigInteger>> organizeZeroOneStructures(final CountingProblem problem, final boolean thin,
			final Map<IntVec,BigInteger> counts) {
		final Map<IntVec,Map<IntVec,BigInteger>> modulusToRhsToZOCount = new HashMap<IntVec,Map<IntVec,BigInteger>>(1000);
		for(final Map.Entry<IntVec,BigInteger> me: counts.entrySet()) {
			final IntVec b = me.getKey();
			final BigInteger c = me.getValue();
			if(c.compareTo(BigInteger.ZERO)>0) {
				final IntVec groupVec = mod2Vec(b);
				boolean use = true;
				if(thin) {
					final int[] groupVecA = groupVec.asVec();
					final Permutation perm = problem.toNormalForm(groupVecA);
					final IntVec sortedGroupVec = new IntVec(perm.apply(groupVecA));
					use = groupVec.compareTo(sortedGroupVec)==0;
				}
				if(use) {
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
		}
		return modulusToRhsToZOCount;
	}
	
	public ZeroOneStore(final CountingProblem problem, final Map<IntVec,BigInteger> counts) {
		this.problem = problem;
		modulusToRhsToZOCount = organizeZeroOneStructures(problem,false,counts);
		modulusToRhsToZOCountThin = organizeZeroOneStructures(problem,true,counts);
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
		{
			final Map<IntVec,BigInteger> stdAnswer = modulusToRhsToZOCount.get(groupVec);
			if((null==stdAnswer)!=(null==mpAnswer)) {
				final int[] groupVecA2 = groupVec.asVec();
				final Permutation perm2 = problem.toNormalForm(groupVecA2);
				final IntVec sortedGroupVec2 = new IntVec(perm.apply(groupVecA2));
				throw new IllegalStateException("different nullity");
			}
			if(null!=stdAnswer) {
				if(stdAnswer.size()!=mpAnswer.size()) {
					throw new IllegalStateException("different size");
				}
				for(final Map.Entry<IntVec,BigInteger> me: stdAnswer.entrySet()) {
					final IntVec keyi = me.getKey();
					final BigInteger vi = me.getValue();
					final BigInteger v2 = mpAnswer.get(keyi);
					if((null==v2)||(vi.compareTo(v2)!=0)) {
						throw new IllegalStateException("different count");
					}
				}
			}
		}
		return mpAnswer;
	}
}
