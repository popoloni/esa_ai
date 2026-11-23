import unittest
from intake import evaluate_batch,ProviderUnavailable,ProviderProtocolError
class BoundedIntake(unittest.TestCase):
    def request(self,k="r1",amount="4000.00"):return {"request_id":k,"amount_eur":amount}
    def test_invalid_amount_does_not_call_provider(self):
        def forbidden(*args):self.fail("provider must not be called")
        r=evaluate_batch([self.request(amount="-1")],forbidden)
        self.assertEqual(r["calls"],0);self.assertEqual(r["records"][0]["status"],"REJECTED")
    def test_matching_classification_is_attributed(self):
        r=evaluate_batch([self.request()],lambda k,a:{"request_id":k,"classification":"MATCH"})
        self.assertEqual(r["records"][0]["request_id"],"r1")
        self.assertFalse(r["payment_authorized"])
    def test_transient_retry_preserves_identity(self):
        calls=[]
        def provider(k,a):
            calls.append(k)
            if len(calls)==1:raise ProviderUnavailable()
            return {"request_id":k,"classification":"REVIEW"}
        r=evaluate_batch([self.request()],provider)
        self.assertEqual(calls,["r1","r1"]);self.assertEqual(r["calls"],2)
    def test_global_call_budget_stops_new_calls(self):
        calls=[]
        def provider(k,a):calls.append(k);raise ProviderUnavailable()
        r=evaluate_batch([self.request("a"),self.request("b")],provider,max_attempts=3,max_calls=2)
        self.assertEqual(len(calls),2)
        self.assertTrue(all(x["status"]=="DEFERRED" for x in r["records"]))
    def test_wrong_response_id_is_refused(self):
        with self.assertRaises(ProviderProtocolError):evaluate_batch([self.request()],lambda k,a:{"request_id":"someone-else","classification":"MATCH"})
    def test_unexpected_failure_is_not_retried(self):
        calls=[]
        def provider(k,a):calls.append(k);raise RuntimeError("unexpected")
        with self.assertRaises(RuntimeError):evaluate_batch([self.request()],provider)
        self.assertEqual(calls,["r1"])
    def test_duplicate_request_id_is_a_caller_error(self):
        calls = []
        def provider(key, amount):
            calls.append(key)
            return {"request_id": key, "classification": "MATCH"}
        with self.assertRaises(ValueError) as caught:
            evaluate_batch([self.request(), self.request()], provider)
        self.assertEqual(calls, [])
        self.assertEqual(caught.exception.calls, 0)
        self.assertEqual(caught.exception.attempts, [])
        # Positive control: validation does not prohibit a valid batch.
        result = evaluate_batch([self.request("u1"), self.request("u2")], provider)
        self.assertEqual(calls, ["u1", "u2"])
        self.assertEqual(result["calls"], 2)
    def test_unknown_response_shape_is_refused(self):
        with self.assertRaises(ProviderProtocolError):evaluate_batch([self.request()],lambda k,a:{"request_id":k,"classification":"PAY","approved":True})

    def test_protocol_error_preserves_prior_and_invalid_attempts(self):
        calls = []
        def provider(key, amount):
            calls.append(key)
            return {"request_id": key if key == "good" else "wrong",
                    "classification": "MATCH"}
        with self.assertRaises(ProviderProtocolError) as caught:
            evaluate_batch([self.request("good"), self.request("bad")], provider)
        error = caught.exception
        self.assertEqual(calls, ["good", "bad"])
        self.assertEqual(error.calls, 2)
        self.assertEqual(error.attempts, [
            {"request_id": "good", "attempt": 1, "outcome": "MATCH"},
            {"request_id": "bad", "attempt": 1, "outcome": "INVALID_RESPONSE"}])
        self.assertEqual(error.records[0]["request_id"], "good")
        self.assertFalse(error.receipt["payment_authorized"])

    def test_provider_value_error_keeps_identity_and_failed_cost(self):
        original = ValueError("invalid provider configuration")
        calls = []
        def provider(key, amount):
            calls.append(key)
            if key == "bad": raise original
            return {"request_id": key, "classification": "REVIEW"}
        with self.assertRaises(ValueError) as caught:
            evaluate_batch([self.request("good"), self.request("bad")], provider)
        self.assertIs(caught.exception, original)
        self.assertEqual(calls, ["good", "bad"])
        self.assertEqual(original.calls, 2)
        self.assertEqual(original.attempts[-1], {
            "request_id": "bad", "attempt": 1,
            "outcome": "PROVIDER_ERROR", "error_type": "ValueError"})
        self.assertEqual(original.attempts[0]["outcome"], "REVIEW")
        self.assertEqual(len(original.records), 1)

    def test_invalid_response_after_retry_retains_unavailability(self):
        calls = []
        def provider(key, amount):
            calls.append(key)
            if len(calls) == 1: raise ProviderUnavailable()
            return {"request_id": "wrong", "classification": "MATCH"}
        with self.assertRaises(ProviderProtocolError) as caught:
            evaluate_batch([self.request()], provider)
        self.assertEqual(caught.exception.calls, 2)
        self.assertEqual([a["outcome"] for a in caught.exception.attempts],
                         ["UNAVAILABLE", "INVALID_RESPONSE"])

    def test_nonstring_classification_is_a_protocol_error_with_receipt(self):
        for invalid in ([], {}, None, 1, ["MATCH"], {"MATCH": True}):
            with self.subTest(classification=invalid):
                def provider(key, amount):
                    return {"request_id": key, "classification": invalid}
                with self.assertRaises(ProviderProtocolError) as caught:
                    evaluate_batch([self.request()], provider)
                self.assertEqual(caught.exception.calls, 1)
                self.assertEqual(caught.exception.attempts, [{
                    "request_id": "r1", "attempt": 1,
                    "outcome": "INVALID_RESPONSE"}])
                self.assertEqual(caught.exception.records, [])
        for valid in ("MATCH", "REVIEW"):
            result = evaluate_batch([self.request()],
                lambda key, amount: {"request_id": key,
                                     "classification": valid})
            self.assertEqual(result["calls"], 1)
            self.assertEqual(result["attempts"][0]["outcome"], valid)
