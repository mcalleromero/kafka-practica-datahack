package com.tm.kafka.connect.rest.http.payload.templated;


import com.tm.kafka.connect.rest.http.Request;
import com.tm.kafka.connect.rest.http.Response;
import org.apache.kafka.common.Configurable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


/**
 * Lookup values used to populate dynamic payloads.
 * These values will be substituted into the payload template.
 *
 * This implementation uses Regular Expressions to extract values from the HTTP response,
 * and if not found looks them up in the System properties and then in environment variables.
 */
public class RegexResponseValueProvider extends EnvironmentValueProvider implements Configurable {

  private static Logger log = LoggerFactory.getLogger(RegexResponseValueProvider.class);

  public static final String MULTI_VALUE_SEPARATOR = ",";

  private Map<String, Pattern> patterns;


  /**
   * Configure this instance after creation.
   *
   * @param props The configuration properties
   */
  @Override
  public void configure(Map<String, ?> props) {
    final RegexResponseValueProviderConfig config = new RegexResponseValueProviderConfig(props);
    setRegexes(config.getResponseVariableRegexs());
  }

  /**
   * Extract values from the response using the regular expressions
   *
   * @param request The last request made.
   * @param response The last response received.
   */
  @Override
  protected void extractValues(Request request, Response response) {
    String resp = response.getPayload();
    patterns.forEach((key, pat) -> parameterMap.put(key, extractValue(key, resp, pat)));
  }

  /**
   * Set the RegExs to be used for value extraction.
   *
   * @param regexes A map of key names to regular expressions
   */
  protected void setRegexes(Map<String, String> regexes) {
    patterns = new HashMap<>(regexes.size());
    parameterMap = new HashMap<>(patterns.size());
    regexes.forEach((k,v) -> patterns.put(k, Pattern.compile(v)));
  }

  /**
   * Extract the value for a given key.
   * Where the RegEx yeilds more than one result a comma seperated list will be returned.
   * If the RegEx has one or more groups then their contents will each be added to the returned list.
   * If the RegEx has no groups then the match for the entire RegEx will be added.
   * If the RegEx matches multiple times then each match will be processed and added to the list (as above).
   *
   * @param key The name of the key
   * @param resp The response to extract a value from
   * @param pattern The compiled RegEx used to find the value
   * @return Return the value, or null if it wasn't found
   */
  private String extractValue(String key, String resp, Pattern pattern) {
    Matcher matcher = pattern.matcher(resp);
    StringBuilder values = new StringBuilder();
    // Iterate over each place where the regex matches
    while(matcher.find()) {
      if(values.length() > 0) {
        values.append(MULTI_VALUE_SEPARATOR);
      }
      if(matcher.groupCount() == 0) {
        // if the regex has no groups then the whole thing is the value
        values.append(matcher.group());
      } else {
        // If the regex has one or more groups then append them in order
        for(int g = 1; g <= matcher.groupCount(); g++) {
          if(g > 1) {
            values.append(MULTI_VALUE_SEPARATOR);
          }
          values.append(matcher.group(g));
        }
      }
    }

    String value = (values.length() != 0) ? values.toString() : null;
    log.info("Variable {} was assigned the value {}", key, value);
    return value;
  }
}
