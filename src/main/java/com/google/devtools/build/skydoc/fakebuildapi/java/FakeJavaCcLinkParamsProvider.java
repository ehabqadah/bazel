// Copyright 2018 The Bazel Authors. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package com.google.devtools.build.skydoc.fakebuildapi.java;

import com.google.devtools.build.lib.skylarkbuildapi.cpp.CcLinkingInfoApi;
import com.google.devtools.build.lib.skylarkbuildapi.java.JavaCcLinkParamsProviderApi;
import com.google.devtools.build.lib.skylarkinterface.SkylarkPrinter;
import com.google.devtools.build.lib.syntax.EvalException;

/** Fake implementation of {@link JavaCcLinkParamsProvider}. */
public class FakeJavaCcLinkParamsProvider implements JavaCcLinkParamsProviderApi<CcLinkingInfoApi> {

  @Override
  public CcLinkingInfoApi getCcLinkingInfo() {
    return null;
  }

  /** Fake implementation of {@link JavaCcLinkParamsProvider#Provider}. */
  public static class Provider implements JavaCcLinkParamsProviderApi.Provider<CcLinkingInfoApi> {

    @Override
    public FakeJavaCcLinkParamsProvider createInfo(CcLinkingInfoApi ccLinkingInfoApi)
        throws EvalException {
      return new FakeJavaCcLinkParamsProvider();
    }

    @Override
    public void repr(SkylarkPrinter printer) {}
  }
}
