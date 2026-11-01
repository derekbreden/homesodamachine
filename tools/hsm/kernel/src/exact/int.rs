//! Checked signed-magnitude integers, with the same limb operations on native and wasm32.
use super::{Error, Result, Sign};
use std::cmp::Ordering;

#[derive(Clone, Copy, PartialEq, Eq, Hash)]
pub(crate) struct Int<const N: usize> {
    negative: bool,
    limbs: [u64; N],
}

impl<const N: usize> Int<N> {
    pub(crate) const ZERO: Self = Self {
        negative: false,
        limbs: [0; N],
    };

    pub(crate) fn from_u128(value: u128) -> Result<Self> {
        let mut out = Self::ZERO;
        if N == 0 {
            return if value == 0 {
                Ok(out)
            } else {
                Err(Error::Overflow)
            };
        }
        out.limbs[0] = value as u64;
        if N > 1 {
            out.limbs[1] = (value >> 64) as u64;
        } else if value >> 64 != 0 {
            return Err(Error::Overflow);
        }
        Ok(out)
    }

    pub(crate) fn from_i128(value: i128) -> Result<Self> {
        let mut out = Self::from_u128(value.unsigned_abs())?;
        out.negative = value < 0;
        Ok(out)
    }

    pub(crate) fn sign(self) -> Sign {
        if self.is_zero() {
            Sign::Zero
        } else if self.negative {
            Sign::Negative
        } else {
            Sign::Positive
        }
    }

    pub(crate) fn is_zero(self) -> bool {
        self.limbs.iter().all(|&x| x == 0)
    }

    pub(crate) fn abs(mut self) -> Self {
        self.negative = false;
        self
    }

    pub(crate) fn negated(mut self) -> Self {
        if !self.is_zero() {
            self.negative = !self.negative;
        }
        self
    }

    fn used(self) -> usize {
        self.limbs
            .iter()
            .rposition(|&x| x != 0)
            .map_or(0, |i| i + 1)
    }

    pub(super) fn magnitude(&self) -> &[u64] {
        &self.limbs[..self.used()]
    }

    pub(super) fn from_magnitude(limbs: &[u64], negative: bool) -> Result<Self> {
        if limbs.len() > N {
            return Err(Error::Overflow);
        }
        let mut out = Self::ZERO;
        out.limbs[..limbs.len()].copy_from_slice(limbs);
        out.negative = negative && !out.is_zero();
        Ok(out)
    }

    pub(crate) fn bit_len(self) -> usize {
        let n = self.used();
        if n == 0 {
            0
        } else {
            64 * (n - 1) + 64 - self.limbs[n - 1].leading_zeros() as usize
        }
    }

    fn cmp_abs(&self, other: &Self) -> Ordering {
        for i in (0..N).rev() {
            match self.limbs[i].cmp(&other.limbs[i]) {
                Ordering::Equal => {}
                order => return order,
            }
        }
        Ordering::Equal
    }

    fn add_abs(self, other: Self) -> Result<Self> {
        let mut out = Self::ZERO;
        let mut carry = 0_u128;
        for i in 0..N {
            let sum = self.limbs[i] as u128 + other.limbs[i] as u128 + carry;
            out.limbs[i] = sum as u64;
            carry = sum >> 64;
        }
        if carry != 0 {
            Err(Error::Overflow)
        } else {
            Ok(out)
        }
    }

    /// Magnitudes only; the caller establishes `self >= other`.
    fn sub_abs(self, other: Self) -> Self {
        let mut out = Self::ZERO;
        let mut borrow = false;
        for i in 0..N {
            let (a, first) = self.limbs[i].overflowing_sub(other.limbs[i]);
            let (b, second) = a.overflowing_sub(u64::from(borrow));
            out.limbs[i] = b;
            borrow = first || second;
        }
        debug_assert!(!borrow);
        out
    }

    pub(crate) fn checked_add(self, other: Self) -> Result<Self> {
        let mut out = if self.negative == other.negative {
            let mut out = self.add_abs(other)?;
            out.negative = self.negative;
            out
        } else {
            match self.cmp_abs(&other) {
                Ordering::Equal => Self::ZERO,
                Ordering::Greater => {
                    let mut out = self.sub_abs(other);
                    out.negative = self.negative;
                    out
                }
                Ordering::Less => {
                    let mut out = other.sub_abs(self);
                    out.negative = other.negative;
                    out
                }
            }
        };
        if out.is_zero() {
            out.negative = false;
        }
        Ok(out)
    }

    pub(crate) fn checked_sub(self, other: Self) -> Result<Self> {
        self.checked_add(other.negated())
    }

    pub(crate) fn checked_mul(self, other: Self) -> Result<Self> {
        let mut out = Self::ZERO;
        let (na, nb) = (self.used(), other.used());
        for i in 0..na {
            if self.limbs[i] == 0 {
                continue;
            }
            let mut carry = 0_u128;
            for j in 0..nb {
                let k = i + j;
                if k >= N {
                    if other.limbs[j] != 0 || carry != 0 {
                        return Err(Error::Overflow);
                    }
                    continue;
                }
                // A product, an output limb and the incoming carry fit exactly in u128.
                let sum =
                    self.limbs[i] as u128 * other.limbs[j] as u128 + out.limbs[k] as u128 + carry;
                out.limbs[k] = sum as u64;
                carry = sum >> 64;
            }
            let mut k = i + nb;
            while carry != 0 {
                if k >= N {
                    return Err(Error::Overflow);
                }
                let sum = out.limbs[k] as u128 + carry;
                out.limbs[k] = sum as u64;
                carry = sum >> 64;
                k += 1;
            }
        }
        out.negative = !out.is_zero() && self.negative != other.negative;
        Ok(out)
    }

    pub(crate) fn checked_shl(self, shift: usize) -> Result<Self> {
        if self.is_zero() {
            return Ok(self);
        }
        if shift > N * 64 || self.bit_len() > N * 64 - shift {
            return Err(Error::Overflow);
        }
        let mut out = Self::ZERO;
        let (whole, bits) = (shift / 64, shift % 64);
        for i in 0..self.used() {
            let k = i + whole;
            out.limbs[k] |= self.limbs[i] << bits;
            if bits != 0 && k + 1 < N {
                out.limbs[k + 1] |= self.limbs[i] >> (64 - bits);
            }
        }
        out.negative = self.negative;
        Ok(out)
    }

    /// Quotient and remainder of nonnegative magnitudes. Signs are deliberately not inferred.
    pub(crate) fn div_rem(self, divisor: Self) -> Result<(Self, Self)> {
        if divisor.is_zero() {
            return Err(Error::ZeroDivisor);
        }
        let (numerator, divisor) = (self.abs(), divisor.abs());
        let (mut quotient, mut remainder) = (Self::ZERO, Self::ZERO);
        for bit in (0..numerator.bit_len()).rev() {
            remainder = remainder.checked_shl(1)?;
            remainder.limbs[0] |= (numerator.limbs[bit / 64] >> (bit % 64)) & 1;
            if remainder.cmp_abs(&divisor) != Ordering::Less {
                remainder = remainder.sub_abs(divisor);
                quotient.limbs[bit / 64] |= 1_u64 << (bit % 64);
            }
        }
        Ok((quotient, remainder))
    }

    pub(crate) fn to_i128(self) -> Result<i128> {
        if self.used() > 2 {
            return Err(Error::Overflow);
        }
        let mut magnitude = self.limbs.first().copied().unwrap_or(0) as u128;
        if N > 1 {
            magnitude |= (self.limbs[1] as u128) << 64;
        }
        if self.negative {
            if magnitude == 1_u128 << 127 {
                Ok(i128::MIN)
            } else {
                i128::try_from(magnitude)
                    .map(|x| -x)
                    .map_err(|_| Error::Overflow)
            }
        } else {
            i128::try_from(magnitude).map_err(|_| Error::Overflow)
        }
    }

    /// Round a signed rational to an integer, including exact half-to-even decisions.
    pub(crate) fn rounded_ratio_i64(self, denominator: Self) -> Result<i64> {
        if denominator.sign() != Sign::Positive {
            return Err(Error::NonPositiveWeight);
        }
        let (mut quotient, remainder) = self.div_rem(denominator)?;
        let half_order = remainder.cmp_abs(&denominator.sub_abs(remainder));
        if half_order == Ordering::Greater
            || (half_order == Ordering::Equal && N > 0 && quotient.limbs[0] & 1 != 0)
        {
            quotient = quotient.checked_add(Self::from_u128(1)?)?;
        }
        if self.negative {
            quotient = quotient.negated();
        }
        i64::try_from(quotient.to_i128()?).map_err(|_| Error::Overflow)
    }

    /// An approximation for search ordering, with no predicate error guarantee.
    pub(crate) fn approximate(self) -> f64 {
        let mut out = 0.0;
        for i in (0..self.used()).rev() {
            out = out * 18446744073709551616.0 + self.limbs[i] as f64;
        }
        if self.negative { -out } else { out }
    }
}

impl<const N: usize> Ord for Int<N> {
    fn cmp(&self, other: &Self) -> Ordering {
        match (self.negative, other.negative) {
            (true, false) => Ordering::Less,
            (false, true) => Ordering::Greater,
            (true, true) => self.cmp_abs(other).reverse(),
            (false, false) => self.cmp_abs(other),
        }
    }
}

impl<const N: usize> PartialOrd for Int<N> {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl<const N: usize> std::fmt::Debug for Int<N> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if self.negative {
            f.write_str("-")?;
        }
        f.write_str("0x")?;
        let used = self.used();
        if used == 0 {
            return f.write_str("0");
        }
        write!(f, "{:x}", self.limbs[used - 1])?;
        for i in (0..used - 1).rev() {
            write!(f, "{:016x}", self.limbs[i])?;
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    type I = Int<16>;

    fn i(value: i128) -> I {
        I::from_i128(value).unwrap()
    }

    #[test]
    fn signed_arithmetic_matches_i128() {
        let mut state = 0x8968_4a2c_1f29_073b_u64;
        for _ in 0..4096 {
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let a = (state as i64) as i128;
            state = state.wrapping_mul(6364136223846793005).wrapping_add(1);
            let b = (state as i64) as i128;
            assert_eq!(i(a).checked_add(i(b)).unwrap().to_i128().unwrap(), a + b);
            assert_eq!(i(a).checked_sub(i(b)).unwrap().to_i128().unwrap(), a - b);
            assert_eq!(i(a).checked_mul(i(b)).unwrap().to_i128().unwrap(), a * b);
            assert_eq!(i(a).cmp(&i(b)), a.cmp(&b));
            let (q, r) = i(a).div_rem(i(b)).unwrap();
            assert_eq!(q.to_i128().unwrap(), a.abs() / b.abs());
            assert_eq!(r.to_i128().unwrap(), a.abs() % b.abs());
        }
        for value in [i128::MIN, i128::MAX, 0, -1, 1] {
            assert_eq!(i(value).to_i128().unwrap(), value);
        }
        assert_eq!(i(-1).checked_add(i(1)).unwrap(), I::ZERO);
        assert_eq!(I::ZERO.negated(), I::ZERO);
    }

    #[test]
    fn full_width_carries_products_division_and_overflow() {
        let one = i(1);
        let a = one.checked_shl(511).unwrap().checked_sub(one).unwrap();
        let square = a.checked_mul(a).unwrap();
        assert_eq!(square.bit_len(), 1022);
        let (q, r) = square.div_rem(a).unwrap();
        assert_eq!((q, r), (a, I::ZERO));
        let top = one.checked_shl(1023).unwrap();
        assert_eq!(top.checked_add(top), Err(Error::Overflow));
        assert_eq!(top.checked_mul(i(2)), Err(Error::Overflow));
        assert_eq!(top.checked_shl(1), Err(Error::Overflow));
        assert_eq!(top.div_rem(top).unwrap(), (one, I::ZERO));
        assert_eq!(one.div_rem(I::ZERO), Err(Error::ZeroDivisor));
        let maximum = top.checked_add(top.checked_sub(one).unwrap()).unwrap();
        assert_eq!(
            maximum.div_rem(top).unwrap(),
            (one, top.checked_sub(one).unwrap())
        );
        assert_eq!(maximum.checked_mul(one).unwrap(), maximum);
        assert_eq!(maximum.checked_add(one), Err(Error::Overflow));
    }

    #[test]
    fn rational_rounding_is_exact_at_halfway_and_far_below_float_precision() {
        for (n, expected) in [
            (1, 0),
            (3, 2),
            (5, 2),
            (7, 4),
            (-1, 0),
            (-3, -2),
            (-5, -2),
            (-7, -4),
        ] {
            assert_eq!(i(n).rounded_ratio_i64(i(2)).unwrap(), expected);
        }
        let denominator = i(1).checked_shl(700).unwrap();
        let half = i(1).checked_shl(699).unwrap();
        assert_eq!(
            half.checked_sub(i(1))
                .unwrap()
                .rounded_ratio_i64(denominator)
                .unwrap(),
            0
        );
        assert_eq!(
            half.checked_add(i(1))
                .unwrap()
                .rounded_ratio_i64(denominator)
                .unwrap(),
            1
        );
        assert_eq!(
            i(i64::MIN as i128).rounded_ratio_i64(i(1)).unwrap(),
            i64::MIN
        );
        assert_eq!(
            i(i64::MAX as i128 + 1).rounded_ratio_i64(i(1)),
            Err(Error::Overflow)
        );
        assert_eq!(i(1).rounded_ratio_i64(i(-1)), Err(Error::NonPositiveWeight));
    }
}
