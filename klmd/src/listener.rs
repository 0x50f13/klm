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


use crate::proto;
use crate::util::log;
use crate::keyboard;

use std::os::unix::net::UnixListener;
use std::io::prelude::*;

const TAG: &'static str = "listener";

//Listeners accept UNIX-socket connections
//and reads to buffer requests. Then it passes
//buffer to protocol handler.
//TODO: check errors in listen
pub fn listen(keyboard: &mut keyboard::Keyboard){
    let listener = UnixListener::bind("/var/run/klmd.sock").unwrap();

    log::i(TAG, "Started listening at /var/run/klmd.sock");

    loop{
        match listener.accept() {
            Ok((mut sock, addr)) => {
                log::d(TAG, &format!("Received connection from {:?} - {:?}", sock, addr));
                let mut size_buffer = [0; 1];
                let mut response = [0; 1];
                sock.read_exact(&mut size_buffer);

                let sz = size_buffer[0];
                if(sz > 0){
                    let mut buffer = Vec::<u8>::with_capacity(sz as usize);
                    sock.read_exact(&mut buffer);
                    let result = proto::proto_handle_message(keyboard, &buffer);
                    response[0] = result.to_u8();
                    sock.write_all(&response);
                } else {
                    log::e(TAG, "Request length is zero. Responding with bad request.");
                    response[0] = proto::ProtoResponse::RESULT_BAD_REQUEST.to_u8();
                    sock.write_all(&response);
                }
            },
            Err(e) => log::e(TAG, &format!("accept: {:?}", e)),
        }
    }
}