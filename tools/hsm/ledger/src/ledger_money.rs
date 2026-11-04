use anyhow::{Context,Result};
use num_bigint::BigInt;
use num_traits::{Signed,Zero};
use serde_json::Value;
use std::cmp::Ordering;

#[derive(Clone,Debug)]
pub struct Decimal{pub coefficient:BigInt,pub scale:u32}
impl Decimal{
    pub fn zero()->Self{Self{coefficient:BigInt::zero(),scale:0}}
    pub fn parse(s:&str)->Result<Self>{
        let(s,exp)=s.split_once(['e','E']).map(|(a,b)|(a.to_owned(),b.parse::<i32>())).unwrap_or((s.to_owned(),Ok(0)));
        let places=s.split_once('.').map(|(_,s)|s.len()as i32).unwrap_or(0)-exp?;
        let mut coefficient=s.replace('.',"").parse::<BigInt>().context("decimal amount")?;
        let scale=if places>=0{places as u32}else{coefficient*=BigInt::from(10).pow((-places)as u32);0};
        Ok(Self{coefficient,scale})
    }
    pub fn value(v:&Value)->Result<Self>{Self::parse(&v.as_str().map(str::to_owned).unwrap_or_else(||v.to_string()))}
    fn at(&self,scale:u32)->BigInt{&self.coefficient*BigInt::from(10).pow(scale-self.scale)}
    pub fn add(&self,other:&Self)->Self{let scale=self.scale.max(other.scale);Self{coefficient:self.at(scale)+other.at(scale),scale}}
    pub fn sub(&self,other:&Self)->Self{let scale=self.scale.max(other.scale);Self{coefficient:self.at(scale)-other.at(scale),scale}}
    pub fn mul(&self,n:i64)->Self{Self{coefficient:&self.coefficient*n,scale:self.scale}}
    pub fn cmp(&self,other:&Self)->Ordering{let scale=self.scale.max(other.scale);self.at(scale).cmp(&other.at(scale))}
    pub fn abs(&self)->Self{Self{coefficient:self.coefficient.abs(),scale:self.scale}}
    pub fn text(&self)->String{
        let negative=self.coefficient.is_negative();let digits=self.coefficient.abs().to_string();
        let digits=format!("{:0>width$}",digits,width=self.scale as usize+1);let at=digits.len()-self.scale as usize;
        format!("{}{}{}",if negative{"-"}else{""},&digits[..at],if self.scale==0{String::new()}else{format!(".{}",&digits[at..])})
    }
    pub fn fixed(&self,places:u32,grouped:bool,plus:bool)->String{
        let mut n=self.coefficient.abs();
        if self.scale>places{
            let divisor=BigInt::from(10).pow(self.scale-places);let remainder=&n%&divisor;let mut quotient=&n/&divisor;
            let twice=remainder*2;if twice>divisor||(twice==divisor&&(&quotient%2)!=BigInt::zero()){quotient+=1;}n=quotient;
        }else{n*=BigInt::from(10).pow(places-self.scale);}
        let digits=format!("{:0>width$}",n.to_string(),width=places as usize+1);let at=digits.len()-places as usize;let whole=&digits[..at];
        let whole:String=if grouped{whole.chars().enumerate().map(|(i,c)|if i>0&&(whole.len()-i)%3==0{format!(",{c}")}else{c.to_string()}).collect()}else{whole.into()};
        format!("{}{}{}",if self.coefficient.is_negative(){"-"}else if plus{"+"}else{""},whole,if places==0{String::new()}else{format!(".{}",&digits[at..])})
    }
    pub fn money(&self)->String{format!("${}",self.fixed(2,true,false))}
}
