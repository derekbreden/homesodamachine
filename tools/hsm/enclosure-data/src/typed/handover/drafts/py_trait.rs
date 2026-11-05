
/// A typed value's Python form, both ways: how a typed function's parameters and result cross the
/// namespace boundary (a wrapper binding Python arguments, or a call into generated code).
///
/// `f64` accepts an int (as `float(x)` would); a parameter that may receive an int which reaches
/// output (a recorded number, text) is a `Num`. `Vec<T>` is a list and `Tup<T>` a tuple of any
/// length; Rust tuples and `[T; N]` are Python tuples; `Option<T>` is `T` or `None`; `()` is `None`.
pub trait Py: Sized {
    fn to_py(&self) -> Result<Val>;
    fn from_py(value: &Val) -> Result<Self>;
}
/// A Python tuple of any length.
#[derive(Clone, Debug, Default, PartialEq)]
pub struct Tup<T>(pub Vec<T>);

impl Py for Val {
    fn to_py(&self) -> Result<Val> {
        Ok(self.clone())
    }
    fn from_py(value: &Val) -> Result<Self> {
        Ok(value.clone())
    }
}
impl Py for f64 {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::Float(*self))
    }
    fn from_py(value: &Val) -> Result<Self> {
        value.num()
    }
}
impl Py for i64 {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::Int(*self))
    }
    fn from_py(value: &Val) -> Result<Self> {
        match value {
            Val::Int(i) => Ok(*i),
            Val::Bool(b) => Ok(i64::from(*b)),
            _ => bail!("expected an int, got {}", value.repr()?),
        }
    }
}
impl Py for bool {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::Bool(*self))
    }
    fn from_py(value: &Val) -> Result<Self> {
        match value {
            Val::Bool(b) => Ok(*b),
            _ => value.truthy(),
        }
    }
}
impl Py for String {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::Str(self.clone()))
    }
    fn from_py(value: &Val) -> Result<Self> {
        match value {
            Val::Str(s) => Ok(s.clone()),
            _ => bail!("expected a str, got {}", value.repr()?),
        }
    }
}
impl Py for () {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::None)
    }
    fn from_py(_: &Val) -> Result<Self> {
        Ok(())
    }
}
impl Py for super::num::Num {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::from(*self))
    }
    fn from_py(value: &Val) -> Result<Self> {
        super::num::Num::of(value)
    }
}
impl<T: Py> Py for Option<T> {
    fn to_py(&self) -> Result<Val> {
        match self {
            Some(v) => v.to_py(),
            None => Ok(Val::None),
        }
    }
    fn from_py(value: &Val) -> Result<Self> {
        match value {
            Val::None => Ok(None),
            _ => Ok(Some(T::from_py(value)?)),
        }
    }
}
impl<T: Py> Py for Vec<T> {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::list(self.iter().map(Py::to_py).collect::<Result<_>>()?))
    }
    fn from_py(value: &Val) -> Result<Self> {
        value.iter()?.iter().map(T::from_py).collect()
    }
}
impl<T: Py> Py for Tup<T> {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::tuple(self.0.iter().map(Py::to_py).collect::<Result<_>>()?))
    }
    fn from_py(value: &Val) -> Result<Self> {
        Ok(Tup(value.iter()?.iter().map(T::from_py).collect::<Result<_>>()?))
    }
}
impl<T: Py, const N: usize> Py for [T; N] {
    fn to_py(&self) -> Result<Val> {
        Ok(Val::tuple(self.iter().map(Py::to_py).collect::<Result<_>>()?))
    }
    fn from_py(value: &Val) -> Result<Self> {
        let items = value.iter()?;
        ensure!(items.len() == N, "expected {N} values, got {}", items.len());
        let typed = items.iter().map(T::from_py).collect::<Result<Vec<T>>>()?;
        typed.try_into().map_err(|_| anyhow::anyhow!("expected {N} values"))
    }
}
macro_rules! py_tuple {
    ($n:literal; $($t:ident $i:tt),+) => {
        impl<$($t: Py),+> Py for ($($t,)+) {
            fn to_py(&self) -> Result<Val> {
                Ok(Val::tuple(vec![$(self.$i.to_py()?),+]))
            }
            fn from_py(value: &Val) -> Result<Self> {
                let items = value.iter()?;
                ensure!(items.len() == $n, "expected {} values, got {}", $n, items.len());
                Ok(($($t::from_py(&items[$i])?,)+))
            }
        }
    };
}
py_tuple!(1; A 0);
py_tuple!(2; A 0, B 1);
py_tuple!(3; A 0, B 1, C 2);
py_tuple!(4; A 0, B 1, C 2, D 3);
py_tuple!(5; A 0, B 1, C 2, D 3, E 4);
py_tuple!(6; A 0, B 1, C 2, D 3, E 4, F 5);
py_tuple!(7; A 0, B 1, C 2, D 3, E 4, F 5, G 6);
py_tuple!(8; A 0, B 1, C 2, D 3, E 4, F 5, G 6, H 7);
/// The Python form of each value, for a call's positional arguments.
#[macro_export]
macro_rules! py_args {
    ($($v:expr),* $(,)?) => {
        vec![$($crate::typed::py::Py::to_py(&$v)?),*]
    };
}
