import base64
import json
import os
import pickle
import sys

import container
from container import Container, NullableContainer, TrackingContainer


SHOULD_RUN = True


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


if __name__ == "__main__":
    print(f"{container.__version__=}")

    c = Container(k=17)
    print(f"{c=}")

    def test_func(k1, k2):
        print(f"{k1=} {k2=}")

    n = NullableContainer({'k1': 1, 'k2': NullableContainer({'nk1': 'fred'})})
    test_func(**n)

    unit_id = 'OORA01WGP'

    if SHOULD_RUN:
        tc = TrackingContainer({'test': 17})

        print(f"{tc.test}")
        try:
            print(f"{tc.foo}")
        except AttributeError:
            print("ignoring attribute error on tc.foo")

        print(f"pre-mod {tc.modifiedKeys=}")
        if "checklistDefinitions" not in tc:
            tc.checklistDefinitions = {}
        tc.checklistDefinitions["a"] = None
        print(f"post-mod {tc.modifiedKeys=}")
        print(f"{repr(tc)=}")
        dill = pickle.dumps(tc)
        sour = pickle.loads(dill)
        print(f"{repr(sour)=}")
        print(f"post-unpickle {sour.modifiedKeys=}")

        print(f"pre-SetAllowedAccesses {tc=} {tc.keys()=} {tc.values()=} {tc.items()=}")

        tc.SetAllowedAccesses({"checklistDefinitions"}, {"checklistDefinitions"})

        print(f"post-SetAllowedAccesses {tc=} {tc.keys()=} {tc.values()=} {tc.items()=}")

        tcc = tc.copy()
        print(f"{tcc=}")

        if "checklistDefinitions" not in tc:
            print("lost")
        else:
            c = Container(Value="hello", v2="test")
            print(f"{pickle.dumps(c)=}")
            print(f"{base64.b64encode(pickle.dumps(tc))=}")
            print(f"{json.dumps(tc)}")

        c = Container(Value="hello", v2="test")
        print("before pickle")
        pc = pickle.dumps(c)
        uc = pickle.loads(pc)
        print("before copy")
        c1 = c.copy()

        nc = NullableContainer(c)
        print(f"{nc=} {nc.foo=}")

        def test_kwargs(*, Value, **kwargs):  # NOSONAR legacy
            print(f"{Value=} {kwargs=}")
        test_kwargs(**nc)

        print(f"{pickle.dumps(nc)=}")
        c.Value = "bye"
        if "Value" in c:
            print("in")
        nc.Value = "goodbye"
        nc1 = NullableContainer()
        print(
            f"{c=} {uc=} {c1=} {nc.Value=} {nc1.Value=} {json.dumps(nc)=} "
            f"{json.dumps(nc1)=}"
        )

        x = Container(samantha="cohen", chris="ditrani", brett="cohen")
        print(f"{x=}")
        print(f"{json.dumps(x)=}")
        x.update({"jeff": Container(j1="robbins", j2="scott")}, other="this")
        print(f"{x=}")

        y = NullableContainer(brett="cohen", gabe="schaffer")
        print("y (initial) =", y)
        y.update(NullableContainer(jeff=NullableContainer(j1="robbins", j2="scott")))
        print("y (post update) =", y)
        print("y.jeff.j1 =", y.jeff.j1)
        print("y.wendy.carson =", y.wendy.carson)

        class AnotherContainer(Container):
            pass

        print(f"{AnotherContainer()=}")
