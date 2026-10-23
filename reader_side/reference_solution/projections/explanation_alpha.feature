Feature: Explain the routing recommendation without authorizing payment
  # Illustrative Gherkin; no Cucumber/Behave runner executed.

  Scenario: SC-EXPL-001
    Given BR-001/v1 routing-only service with a separate human payment authorization process
    When an operator requests an explanation for amount 4999.99
    Then return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

  Scenario: SC-EXPL-002
    Given BR-001/v1 routing-only service with a separate human payment authorization process
    When an operator requests an explanation for amount 5000
    Then return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

  Scenario: SC-EXPL-003
    Given BR-001/v1 routing-only service with a separate human payment authorization process
    When an operator requests an explanation for amount 5000.01
    Then return routing HUMAN_REVIEW with reason AT_OR_ABOVE_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

  Scenario: SC-EXPL-004
    Given BR-001/v1 routing-only service with a separate human payment authorization process
    When an operator requests an explanation for amount 0
    Then return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

  Scenario: SC-EXPL-005
    Given BR-001/v1 routing-only service with a separate human payment authorization process
    When an operator requests an explanation for amount -10
    Then return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

  Scenario: SC-EXPL-006
    Given BR-001/v1 routing-only service with a separate human payment authorization process
    When an operator requests an explanation for amount nonsense
    Then return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

  Scenario: SC-EXPL-007
    Given BR-001/v1 routing-only service with a separate human payment authorization process
    When an operator requests an explanation for amount NaN
    Then return routing REJECTED with reason INVALID_AMOUNT, BR-001/v1 and an explicit no-payment-approval notice

  Scenario: SC-EXPL-008
    Given BR-001/v1 routing-only service with a separate human payment authorization process
    When an operator requests an explanation for amount 1
    Then return routing STANDARD_QUEUE with reason BELOW_LIMIT, BR-001/v1 and an explicit no-payment-approval notice

