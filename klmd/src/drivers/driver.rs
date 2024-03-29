/**
 * This file is part of KLMd project.
 *
 *  Copyright 2022 by Polar <toddot@protonmail.com>
 *
 *  Licensed under GNU General Public License 3.0 or later.
 *  Some rights reserved. See COPYING, AUTHORS.
 *
 * @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
 */

use crate::util::color;
use crate::util::u8::U8Serializable;

//use hidapi::HidApi;

#[derive(Clone)]
pub enum KeyboardMode {
    ModeSteady,
    ModeBreathing,
    ModeColorshift,
}

impl U8Serializable for KeyboardMode {
    fn to_u8(&self) -> u8 {
        match *self {
            KeyboardMode::ModeSteady => 0x1,
            KeyboardMode::ModeBreathing => 0x2,
            KeyboardMode::ModeColorshift => 0x3,
        }
    }
}

pub trait Driver {
    fn new(api: &hidapi::HidApi) -> Option<Self> where Self: Sized;
    fn is_present(api: &hidapi::HidApi) -> bool where Self: Sized;
    fn set_color(&self, color: &color::RGB, brightness: u8) -> bool;
    fn set_breathing(&self, colors: &Vec<color::RGB>, brightness: u8, speed: u8) -> bool;
    fn set_shift(&self, colors: &Vec<color::RGB>, brightness: u8, speed: u8) -> bool;
    fn set_power(&self, value: bool) -> bool;
    fn get_modes(&self) -> Vec<KeyboardMode>;
    fn get_max_colors(&self) -> u8;
}
