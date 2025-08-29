const synthetics = require("Synthetics");
const log = require("SyntheticsLogger");

const canaryTest = async function () {
  let request = new synthetics.HttpRequest("https://example.com/");
  let response = await synthetics.executeHttpStep("VerifyHomepage", request);
  log.info("Status Code: " + response.statusCode);
};

exports.handler = async () => {
  return await canaryTest();
};
