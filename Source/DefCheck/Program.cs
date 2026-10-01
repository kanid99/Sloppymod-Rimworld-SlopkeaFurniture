// Checks mod XML against RimWorld's own types, the way DirectXmlToObject does:
// every element must name a field on the type it lands in.
using System; using System.Linq; using System.Reflection; using System.IO; using System.Xml; using System.Collections.Generic;
var dir="/root/.nuget/packages/krafs.rimworld.ref/1.6.4871/ref/net472/";
var paths=Directory.GetFiles(dir,"*.dll").Concat(Directory.GetFiles("/root/.nuget/packages/microsoft.netframework.referenceassemblies.net472/1.0.3/build/.NETFramework/v4.7.2/","*.dll")).GroupBy(Path.GetFileName).Select(g=>g.First());
using var ctx=new MetadataLoadContext(new PathAssemblyResolver(paths));
var asm=ctx.LoadFromAssemblyPath(dir+"Assembly-CSharp.dll");
var types=asm.GetTypes();
Type ByName(string n)=>types.FirstOrDefault(t=>t.FullName==n)??types.FirstOrDefault(t=>t.Name==n);
var all=new List<XmlElement>(); var named=new Dictionary<string,XmlElement>();
foreach(var f in args) { var d=new XmlDocument(); d.Load(f); foreach(XmlNode n in d.DocumentElement.ChildNodes) if(n is XmlElement e){ all.Add(e); var nm=e.GetAttribute("Name"); if(nm!="") named[nm]=e; } }
int errors=0;
FieldInfo Field(Type t,string name){ for(var c=t;c!=null;c=c.BaseType){ try{
  foreach(var f in c.GetFields(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.DeclaredOnly)){
    if(f.Name==name) return f;
    // [LoadAlias("x")] lets the XML name a field by another name.
    foreach(var ca in f.GetCustomAttributesData())
      if(ca.AttributeType.Name=="LoadAliasAttribute" && ca.ConstructorArguments.Count>0 && (string)ca.ConstructorArguments[0].Value==name) return f; }
  }catch{} } return null; }
bool IsDict(Type t)=>t.IsGenericType && t.GetGenericTypeDefinition().Name.StartsWith("Dictionary");
bool Leafy(Type t)=>t.IsPrimitive||t.IsEnum||t.Name=="String"||t.Name.StartsWith("IntVec")||t.Name.StartsWith("Vector")||t.Name=="Color"||t.Name=="Type"||t.Name=="FloatRange"||t.Name=="IntRange"||typeof(object)!=null&&IsDefRef(t);
bool IsDefRef(Type t){ for(var c=t;c!=null;c=c.BaseType) if(c.FullName=="Verse.Def") return true; return false; }
void Check(XmlElement e,Type t,string where){
  foreach(XmlNode n in e.ChildNodes){ if(n is not XmlElement c) continue;
    var f=Field(t,c.Name);
    if(f==null){ Console.WriteLine($"{where}: <{c.Name}> is not a field of {t.FullName}"); errors++; continue; }
    var ft=f.FieldType;
    if(ft.IsGenericType && ft.GetGenericTypeDefinition().Name.StartsWith("List")){
      var it=ft.GetGenericArguments()[0];
      if(IsDefRef(it)||Leafy(it)) continue;
      foreach(XmlNode li in c.ChildNodes){ if(li is not XmlElement le) continue;
        var cls=le.GetAttribute("Class"); var lt=cls!=""?ByName(cls):it;
        if(lt==null){ Console.WriteLine($"{where}.{c.Name}: no class {cls}"); errors++; continue; }
        if(le.ChildNodes.OfType<XmlElement>().Any()) Check(le,lt,where+"."+c.Name+"["+lt.Name+"]"); }
      continue; }
    if(IsDict(ft)||Leafy(ft)||ft.Name=="StatModifier"||c.ChildNodes.OfType<XmlElement>().Count()==0) continue;
    var cls2=c.GetAttribute("Class"); Check(c, cls2!=""?ByName(cls2):ft, where+"."+c.Name);
  } }
// Resolve inheritance the simple way: a def's fields plus its parents' (each checked on its own).
foreach(var e in all){
  if(e.Name=="Operation"){ continue; }
  var t=ByName(e.Name); if(t==null){ Console.WriteLine($"no def type {e.Name}"); errors++; continue; }
  var id=e.SelectSingleNode("defName")?.InnerText ?? e.GetAttribute("Name");
  Check(e,t,id);
}
Console.WriteLine(errors==0?"defs ok: every field exists in RimWorld 1.6":$"{errors} error(s)"); return errors==0?0:1;
