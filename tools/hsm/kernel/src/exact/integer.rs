//! Exact integers with checked inline operations and an unbounded limb fallback.
//!
//! Repeated booleans and binary64 affine maps do not have a fixed bit budget. The inline type
//! is an optimization, not a precision limit on retained geometry.
use super::{Error, Result, Sign, Wide};
use std::cmp::Ordering;

#[derive(Clone, PartialEq, Eq, Hash)]
enum Repr {
    Inline(Wide),
    Heap { negative: bool, limbs: Vec<u64> },
}

#[derive(Clone, PartialEq, Eq, Hash)]
pub(crate) struct Integer(Repr);

impl Integer {
    pub(crate) const ZERO: Self = Self(Repr::Inline(Wide::ZERO));

    pub(crate) fn from_i128(value: i128) -> Self {
        Self(Repr::Inline(
            Wide::from_i128(value).expect("i128 fits the inline integer"),
        ))
    }

    fn from_parts(mut limbs: Vec<u64>, negative: bool) -> Self {
        while limbs.last() == Some(&0) {
            limbs.pop();
        }
        if let Ok(value) = Wide::from_magnitude(&limbs, negative) {
            Self(Repr::Inline(value))
        } else {
            Self(Repr::Heap { negative, limbs })
        }
    }

    fn magnitude(&self) -> &[u64] {
        match &self.0 {
            Repr::Inline(value) => value.magnitude(),
            Repr::Heap { limbs, .. } => limbs,
        }
    }

    fn negative(&self) -> bool {
        match &self.0 {
            Repr::Inline(value) => value.sign() == Sign::Negative,
            Repr::Heap { negative, .. } => *negative,
        }
    }

    pub(crate) fn is_zero(&self) -> bool {
        self.magnitude().is_empty()
    }

    pub(crate) fn sign(&self) -> Sign {
        if self.is_zero() {
            Sign::Zero
        } else if self.negative() {
            Sign::Negative
        } else {
            Sign::Positive
        }
    }

    pub(crate) fn negated(&self) -> Self {
        match &self.0 {
            Repr::Inline(value) => Self(Repr::Inline(value.negated())),
            Repr::Heap { negative, limbs } => Self(Repr::Heap {
                negative: !negative,
                limbs: limbs.clone(),
            }),
        }
    }

    pub(crate) fn abs(&self) -> Self {
        if self.negative() {
            self.negated()
        } else {
            self.clone()
        }
    }

    fn cmp_abs(&self, other: &Self) -> Ordering {
        let (a, b) = (self.magnitude(), other.magnitude());
        a.len()
            .cmp(&b.len())
            .then_with(|| a.iter().rev().cmp(b.iter().rev()))
    }

    pub(crate) fn add(&self, other: &Self) -> Self {
        if let (Repr::Inline(a), Repr::Inline(b)) = (&self.0, &other.0) {
            if let Ok(value) = a.checked_add(*b) {
                return Self(Repr::Inline(value));
            }
        }
        let (a, b) = (self.magnitude(), other.magnitude());
        if self.negative() == other.negative() {
            let mut limbs = Vec::with_capacity(a.len().max(b.len()) + 1);
            let mut carry = 0_u128;
            for i in 0..a.len().max(b.len()) {
                let sum = a.get(i).copied().unwrap_or(0) as u128
                    + b.get(i).copied().unwrap_or(0) as u128
                    + carry;
                limbs.push(sum as u64);
                carry = sum >> 64;
            }
            if carry != 0 {
                limbs.push(carry as u64);
            }
            Self::from_parts(limbs, self.negative())
        } else {
            let (a, b, negative) = match self.cmp_abs(other) {
                Ordering::Equal => return Self::ZERO,
                Ordering::Greater => (a, b, self.negative()),
                Ordering::Less => (b, a, other.negative()),
            };
            let mut limbs = Vec::with_capacity(a.len());
            let mut borrow = false;
            for (i, &limb) in a.iter().enumerate() {
                let (first, b1) = limb.overflowing_sub(b.get(i).copied().unwrap_or(0));
                let (second, b2) = first.overflowing_sub(u64::from(borrow));
                limbs.push(second);
                borrow = b1 || b2;
            }
            debug_assert!(!borrow);
            Self::from_parts(limbs, negative)
        }
    }

    pub(crate) fn sub(&self, other: &Self) -> Self {
        self.add(&other.negated())
    }

    pub(crate) fn mul(&self, other: &Self) -> Self {
        if let (Repr::Inline(a), Repr::Inline(b)) = (&self.0, &other.0) {
            if let Ok(value) = a.checked_mul(*b) {
                return Self(Repr::Inline(value));
            }
        }
        let (a, b) = (self.magnitude(), other.magnitude());
        let mut limbs = vec![0; a.len() + b.len()];
        for (i, &x) in a.iter().enumerate() {
            let mut carry = 0_u128;
            for (j, &y) in b.iter().enumerate() {
                let k = i + j;
                let sum = x as u128 * y as u128 + limbs[k] as u128 + carry;
                limbs[k] = sum as u64;
                carry = sum >> 64;
            }
            if !b.is_empty() {
                // No earlier multiplication row reaches this position.
                limbs[i + b.len()] = carry as u64;
            }
        }
        Self::from_parts(limbs, self.negative() != other.negative())
    }

    pub(crate) fn shl(&self, shift: usize) -> Self {
        if let Repr::Inline(value) = self.0 {
            if let Ok(value) = value.checked_shl(shift) {
                return Self(Repr::Inline(value));
            }
        }
        if self.is_zero() {
            return Self::ZERO;
        }
        let (whole, bits) = (shift / 64, shift % 64);
        let magnitude = self.magnitude();
        let mut limbs = vec![0; magnitude.len() + whole + usize::from(bits != 0)];
        for (i, &x) in magnitude.iter().enumerate() {
            limbs[i + whole] |= x << bits;
            if bits != 0 {
                limbs[i + whole + 1] |= x >> (64 - bits);
            }
        }
        Self::from_parts(limbs, self.negative())
    }

    pub(crate) fn shr(&self, shift: usize) -> Self {
        let (whole, bits) = (shift / 64, shift % 64);
        let magnitude = self.magnitude();
        if whole >= magnitude.len() {
            return Self::ZERO;
        }
        let mut limbs = vec![0; magnitude.len() - whole];
        for i in whole..magnitude.len() {
            limbs[i - whole] |= magnitude[i] >> bits;
            if bits != 0 && i + 1 < magnitude.len() {
                limbs[i - whole] |= magnitude[i + 1] << (64 - bits);
            }
        }
        Self::from_parts(limbs, self.negative())
    }

    pub(crate) fn bit_len(&self) -> usize {
        let limbs = self.magnitude();
        limbs.last().map_or(0, |top| {
            64 * (limbs.len() - 1) + 64 - top.leading_zeros() as usize
        })
    }

    fn trailing_zeros(&self) -> usize {
        for (i, &x) in self.magnitude().iter().enumerate() {
            if x != 0 {
                return i * 64 + x.trailing_zeros() as usize;
            }
        }
        0
    }

    /// Nonnegative quotient and remainder of the arguments' magnitudes.
    pub(crate) fn div_rem(&self, divisor: &Self) -> Result<(Self, Self)> {
        if divisor.is_zero() {
            return Err(Error::ZeroDivisor);
        }
        if let (Repr::Inline(a), Repr::Inline(b)) = (&self.0, &divisor.0) {
            let (q, r) = a.div_rem(*b)?;
            return Ok((Self(Repr::Inline(q)), Self(Repr::Inline(r))));
        }
        let numerator = self.magnitude();
        let divisor = divisor.abs();
        let mut quotient = vec![0; numerator.len()];
        let mut remainder = Self::ZERO;
        for bit in (0..self.bit_len()).rev() {
            remainder = remainder.shl(1);
            if (numerator[bit / 64] >> (bit % 64)) & 1 != 0 {
                remainder = remainder.add(&Self::from_i128(1));
            }
            if remainder >= divisor {
                remainder = remainder.sub(&divisor);
                quotient[bit / 64] |= 1_u64 << (bit % 64);
            }
        }
        Ok((Self::from_parts(quotient, false), remainder))
    }

    pub(crate) fn gcd(&self, other: &Self) -> Self {
        let (mut a, mut b) = (self.abs(), other.abs());
        if a.is_zero() {
            return b;
        }
        if b.is_zero() {
            return a;
        }
        let shift = a.trailing_zeros().min(b.trailing_zeros());
        a = a.shr(a.trailing_zeros());
        while !b.is_zero() {
            b = b.shr(b.trailing_zeros());
            if a > b {
                std::mem::swap(&mut a, &mut b);
            }
            b = b.sub(&a);
        }
        a.shl(shift)
    }

    /// Divide by an established factor, retaining this integer's sign.
    pub(crate) fn divided_exactly(&self, factor: &Self) -> Result<Self> {
        let (q, r) = self.div_rem(factor)?;
        if !r.is_zero() {
            return Err(Error::InexactDivision);
        }
        Ok(if self.negative() != factor.negative() {
            q.negated()
        } else {
            q
        })
    }

    pub(crate) fn to_i128(&self) -> Result<i128> {
        match &self.0 {
            Repr::Inline(value) => value.to_i128(),
            Repr::Heap { .. } => Err(Error::Overflow),
        }
    }

    fn rounded_quotient(&self, denominator: &Self) -> Result<Self> {
        if denominator.sign() != Sign::Positive {
            return Err(Error::NonPositiveWeight);
        }
        let (q, r) = self.div_rem(denominator)?;
        let order = r.cmp(&denominator.sub(&r));
        let odd = q.magnitude().first().is_some_and(|x| x & 1 != 0);
        Ok(
            if order == Ordering::Greater || (order == Ordering::Equal && odd) {
                q.add(&Self::from_i128(1))
            } else {
                q
            },
        )
    }

    pub(crate) fn rounded_ratio_i64(&self, denominator: &Self) -> Result<i64> {
        let q = self.rounded_quotient(denominator)?;
        let value = if self.negative() { q.negated() } else { q };
        i64::try_from(value.to_i128()?).map_err(|_| Error::Overflow)
    }

    /// Correctly rounded binary64, constructed from bits without platform transcendental math.
    pub(crate) fn ratio_binary64(&self, denominator: &Self) -> Result<f64> {
        if denominator.sign() != Sign::Positive {
            return Err(Error::NonPositiveWeight);
        }
        let sign = u64::from(self.negative()) << 63;
        if self.is_zero() {
            return Ok(0.0);
        }
        let n = self.abs();
        let mut exponent = n.bit_len() as i128 - denominator.bit_len() as i128;
        let order = if exponent >= 0 {
            n.cmp(&denominator.shl(exponent as usize))
        } else {
            n.shl((-exponent) as usize).cmp(denominator)
        };
        if order == Ordering::Less {
            exponent -= 1;
        }
        if exponent > 1023 {
            return Ok(f64::from_bits(sign | (0x7ff_u64 << 52)));
        }
        if exponent < -1075 {
            return Ok(f64::from_bits(sign));
        }
        if exponent < -1022 {
            let q = n.shl(1074).rounded_quotient(denominator)?;
            return Ok(f64::from_bits(sign | q.to_i128()? as u64));
        }
        let shift = 52 - exponent;
        let rounded = if shift >= 0 {
            n.shl(shift as usize).rounded_quotient(denominator)?
        } else {
            n.rounded_quotient(&denominator.shl((-shift) as usize))?
        };
        let mut significand = rounded.to_i128()? as u64;
        if significand == 1_u64 << 53 {
            significand >>= 1;
            exponent += 1;
            if exponent > 1023 {
                return Ok(f64::from_bits(sign | (0x7ff_u64 << 52)));
            }
        }
        Ok(f64::from_bits(
            sign | ((exponent + 1023) as u64) << 52 | (significand - (1_u64 << 52)),
        ))
    }
}

impl Ord for Integer {
    fn cmp(&self, other: &Self) -> Ordering {
        match (self.negative(), other.negative()) {
            (true, false) => Ordering::Less,
            (false, true) => Ordering::Greater,
            (true, true) => self.cmp_abs(other).reverse(),
            (false, false) => self.cmp_abs(other),
        }
    }
}

impl PartialOrd for Integer {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl std::fmt::Debug for Integer {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if self.negative() {
            f.write_str("-")?;
        }
        f.write_str("0x")?;
        let limbs = self.magnitude();
        if let Some(last) = limbs.last() {
            write!(f, "{:x}", last)?;
            for limb in limbs[..limbs.len() - 1].iter().rev() {
                write!(f, "{:016x}", limb)?;
            }
            Ok(())
        } else {
            f.write_str("0")
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn i(value: i128) -> Integer {
        Integer::from_i128(value)
    }

    #[test]
    fn fallback_retains_every_bit_and_reduces_back_to_inline() {
        let a = i(1).shl(1500).sub(&i(1));
        let b = i(1).shl(1100).add(&i(3));
        let product = a.mul(&b);
        let (q, r) = product.div_rem(&a).unwrap();
        assert_eq!((q, r), (b.clone(), Integer::ZERO));
        assert_eq!(product.negated().divided_exactly(&a).unwrap(), b.negated());
        assert_eq!(a.add(&a.negated()), Integer::ZERO);
        assert_eq!(a.gcd(&product), a);
        assert_eq!(b.sub(&b.sub(&i(17))).to_i128().unwrap(), 17);
    }

    #[test]
    fn binary64_rounding_handles_normal_subnormal_ties_and_overflow() {
        for (n, d) in [(1, 3), (-1, 3), (10, 7), (i64::MAX as i128, 13)] {
            assert_eq!(
                i(n).ratio_binary64(&i(d)).unwrap().to_bits(),
                (n as f64 / d as f64).to_bits()
            );
        }
        let denominator = i(1).shl(1074);
        assert_eq!(i(1).ratio_binary64(&denominator).unwrap().to_bits(), 1);
        assert_eq!(
            i(-1).ratio_binary64(&denominator.shl(2)).unwrap().to_bits(),
            1_u64 << 63
        );
        assert_eq!(
            i(1).ratio_binary64(&denominator.shl(1)).unwrap().to_bits(),
            0
        );
        assert_eq!(
            i(3).ratio_binary64(&denominator.shl(1)).unwrap().to_bits(),
            2
        );
        assert_eq!(i(1).shl(1024).ratio_binary64(&i(1)).unwrap(), f64::INFINITY);
        let halfway = i(1).shl(53).add(&i(1));
        assert_eq!(
            halfway.ratio_binary64(&i(1).shl(53)).unwrap().to_bits(),
            1.0_f64.to_bits()
        );
        assert_eq!(
            halfway
                .add(&i(1))
                .ratio_binary64(&i(1).shl(53))
                .unwrap()
                .to_bits(),
            1.0_f64.to_bits() + 1
        );
    }
}
