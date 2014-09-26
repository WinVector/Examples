package com.mzlabs.fit;

public final class BalanceJacobianCoef {
	public final double balanceCoef;
	public final double jacobianCoef;
	
	public BalanceJacobianCoef(final double balanceCoef, final double jacobianCoef) {
		this.balanceCoef = balanceCoef;
		this.jacobianCoef = jacobianCoef;
	}

	public double absDiff(final BalanceJacobianCoef o) {
		return Math.abs(balanceCoef-o.balanceCoef) + Math.abs(jacobianCoef-jacobianCoef);
	}
	
	@Override
	public String toString() {
		return "g:" + balanceCoef + " h:" + jacobianCoef;
	}
}
