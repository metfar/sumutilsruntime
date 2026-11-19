#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#pylint:disable=W0301
#  
#  Copyright 2018- William Martinez Bas <metfar@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  

import math;

from sumutilsruntime import (
    deg2gon,
    deg2gra,
    deg2rad,
    gon2deg,
    gra2deg,
    gra2rad,
    inspectBlocks,
    rad2deg,
    rad2gon,
    rad2gra,
    serializeInBlocks,
    unserializeInBlocks,
);


def test_angular_conversions():
    assert math.isclose(deg2rad(180), math.pi);
    assert math.isclose(rad2deg(math.pi / 2), 90.0);
    assert math.isclose(deg2gra(90), 100.0);
    assert math.isclose(gra2deg(100), 90.0);
    assert math.isclose(gra2rad(100), math.pi / 2);
    assert math.isclose(rad2gra(math.pi / 2), 100.0);
    assert math.isclose(deg2gon(90), 100.0);
    assert math.isclose(gon2deg(100), 90.0);
    assert math.isclose(rad2gon(math.pi / 2), 100.0);


def test_sumblock_roundtrip():
    original = {"name": "SUM", "values": [1, 2, 3]};
    blocks = serializeInBlocks(original, chunk_size=12);
    status = inspectBlocks(blocks);
    assert status["status"] == "COMPLETE";
    assert unserializeInBlocks(blocks) == original;
