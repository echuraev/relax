# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import tvm
import tvm.testing
from tvm.script import relax as R, tir as T
from tvm.relax.analysis import estimate_memory_usage


def test_basic():
    @tvm.script.ir_module
    class Module:
        @T.prim_func
        def add(
            rxplaceholder: T.Buffer[T.int64(8), "float32"],
            rxplaceholder_1: T.Buffer[(), "float32"],
            T_add: T.Buffer[T.int64(8), "float32"],
        ):
            T.evaluate(0)

        @T.prim_func
        def reshape(
            rxplaceholder: T.Buffer[(T.int64(2), T.int64(4)), "float32"],
            T_reshape: T.Buffer[T.int64(8), "float32"],
        ):
            T.evaluate(0)

        @T.prim_func
        def relu(
            rxplaceholder: T.Buffer[T.int64(8), "float32"], compute: T.Buffer[T.int64(8), "float32"]
        ):
            T.evaluate(0)

        @T.prim_func
        def log(
            rxplaceholder: T.Buffer[T.int64(10), "float32"],
            compute: T.Buffer[T.int64(10), "float32"],
        ):
            T.evaluate(0)

        @T.prim_func
        def exp(
            rxplaceholder: T.Buffer[(T.int64(2), T.int64(4)), "float32"],
            compute: T.Buffer[(T.int64(2), T.int64(4)), "float32"],
        ):
            T.evaluate(0)

        @T.prim_func
        def pad(
            rxplaceholder: T.Buffer[T.int64(8), "float32"],
            PadInput: T.Buffer[T.int64(10), "float32"],
        ):
            T.evaluate(0)

        @R.function
        def main(x: R.Tensor((2, 4), dtype="float32")) -> R.Tensor((10,), dtype="float32"):
            storage: R.Object = R.memory.alloc_storage(
                (32,), virtual_device_index=0, storage_scope="global", dtype="float32"
            )
            alloc: R.Tensor((2, 4), dtype="float32") = R.memory.alloc_tensor(
                storage, offset=0, shape=(2, 4), dtype="float32"
            )
            _: R.Tuple() = exp(x, alloc)
            lv: R.Tensor((2, 4), dtype="float32") = alloc
            lv1: R.Tensor((8,), dtype="float32") = R.call_packed(
                "vm.builtin.reshape", lv, (8,), sinfo_args=[R.Tensor((8,), dtype="float32")]
            )
            storage1: R.Object = R.memory.alloc_storage(
                (40,), virtual_device_index=0, storage_scope="global", dtype="float32"
            )
            alloc1: R.Tensor((8,), dtype="float32") = R.memory.alloc_tensor(
                storage1, offset=0, shape=(8,), dtype="float32"
            )
            _1: R.Tuple() = relu(lv1, alloc1)
            _2: R.Tuple() = R.memory.kill_tensor(alloc)
            _3: R.Tuple() = R.memory.kill_tensor(lv1)
            lv2: R.Tensor((8,), dtype="float32") = alloc1
            alloc2: R.Tensor((8,), dtype="float32") = R.memory.alloc_tensor(
                storage, offset=0, shape=(8,), dtype="float32"
            )
            _4: R.Tuple() = add(lv2, R.const(1, "float32"), alloc2)
            _5: R.Tuple() = R.memory.kill_tensor(alloc1)
            lv3: R.Tensor((8,), dtype="float32") = alloc2
            alloc3: R.Tensor((10,), dtype="float32") = R.memory.alloc_tensor(
                storage1, offset=0, shape=(10,), dtype="float32"
            )
            _6: R.Tuple() = pad(lv3, alloc3)
            _7: R.Tuple() = R.memory.kill_tensor(alloc2)
            lv4: R.Tensor((10,), dtype="float32") = alloc3
            alloc4: R.Tensor((10,), dtype="float32") = R.builtin.alloc_tensor(
                (10,), dtype="float32", runtime_device_index=0
            )
            _8: R.Tuple() = log(lv4, alloc4)
            _9: R.Tuple() = R.memory.kill_tensor(alloc3)
            gv5: R.Tensor((10,), dtype="float32") = alloc4
            _11: R.Tuple() = R.memory.kill_storage(storage)
            _10: R.Tuple() = R.memory.kill_storage(storage1)
            return gv5

    assert (
        estimate_memory_usage(Module)
        == r"""Memory usage estimation:
- Function main:
 * Without memory planning, there are 5 constant-size memory allocation(s) with total size 1.639e-07 GB.
 * With memory planning, there are 2 constant-size memory allocation(s) with total size 6.706e-08 GB.
 * Memory planning reduces constant memory size to 40.9%."""
    )


if __name__ == "__main__":
    tvm.testing.main()
